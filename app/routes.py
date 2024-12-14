from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session, make_response
from .decorators import login_required
from .models import User, db, Post, Vote
from .regusers import api_routes as regusers_blueprint
from flask_wtf.csrf import CSRFProtect, generate_csrf
from .positive_optimistic_blocker import generate_action_token



api_routes = Blueprint('api', __name__)

api_routes.register_blueprint(regusers_blueprint)



@api_routes.route('/')
def home():
    return render_template('base.html')


@api_routes.route('/register')
def register_page():
    return render_template('register.html')


@api_routes.route('/login')
def login():
    return render_template('login.html')


@api_routes.route('/api/greet', methods=['GET'])
def greet():
    return jsonify({"message": "Hello World"})


@api_routes.route('/api/users', methods=['GET'])
def get_users_route():
    users = User.get_all_users()
    users_list = [{"id": user.id, "username": user.username, "name": user.name, "age": user.age, "rating": user.rating, "role": user.role} for user in users]
    return jsonify(users_list)


@api_routes.route('/api/data', methods=['POST'])
def save_data():
    data = request.get_json()
    username = data.get('username')
    password_hash = data.get('password')
    name = data.get('name')
    age = data.get('age')
    rating = data.get('rating')

    if not username or not password_hash or not name or not age or not rating:
        return jsonify({"error": "All fields are required"}), 400

    new_user = User(username=username, password_hash=password_hash, name=name, age=age, rating=rating)
    new_user.save()
    return jsonify({"message": "Data saved successfully"}), 201


@api_routes.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    username = data.get('username')
    rating = data.get('rating')

    if not name and not age and not rating and not username:
        return jsonify({'error': 'At least one field (name, age, or rating) must be provided'}), 400

    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if name:
        user.name = name
    if age:
        user.age = age
    if rating:
        user.rating = rating
    if username:
        user.username = username

    db.session.commit()
    return jsonify({"message": "User updated successfully"})


@api_routes.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('api.login'))

    if request.method == 'POST':
        user.name = request.form.get('name')
        user.age = request.form.get('age')
        user.rating = request.form.get('rating')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('.user_profile', username=username))
    return render_template('user_profile.html', user=user)


@api_routes.route('/feed', methods=['GET', 'POST'])
@login_required
def feed():
    if request.method == 'POST':
        if 'user' not in session:
            return redirect(url_for('api.login'))

        content = request.form['content']
        if len(content) > 250:
            flash('max range of post 250 char', 'error')
            return redirect('api.feed')
        user = User.query.filter_by(username=session['user']).first()
        new_post = Post(content=content, user_id=user.id)
        db.session.add(new_post)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('api.feed'))
        return redirect(url_for('api.feed'))

    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('feed.html', posts=posts)


@api_routes.route('/user/<username>/posts')
@login_required
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    return render_template('user_posts.html', user=user, posts=posts)


csrf = CSRFProtect()

@api_routes.route('/api/feed', methods=['GET', 'POST'])
def get_feed():
    if request.method == 'POST':
        csrf._csrf_disable = True
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Invalid request'}), 400

        content = data['content']
        new_post = Post(content=content, user_id=777)
        db.session.add(new_post)
        try:
            db.session.commit()
            return jsonify({'message': 'Post created successfully!'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    posts = Post.query.order_by(Post.timestamp.desc()).all()
    response = [{'id': post.id,
                 'author': post.author.username,
                 'timestamp': post.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                 'content': post.content,
                 'rating':post.post_rating} for post in posts]
    return jsonify(response)



@api_routes.route('/api/token', methods=['GET'])
def get_csrf_token():
    token = generate_csrf()
    response = make_response(jsonify({'csrf_token': token}))
    response.set_cookie('csrf_token', token)
    return response



@api_routes.route('/rate-post/<int:post_id>/<string:action>/', methods=['POST'])
@login_required
def rate_post(post_id, action):
    post = Post.query.get_or_404(post_id)
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': 'User not looged in'}), 401

    #created token for blocker
    action_token = generate_action_token(user_id, post_id, action)
    existing_token = Vote.query.filter_by(action_token=action_token).first()

    if existing_token:
        return jsonify({'error': 'This action is already in progress'}), 409

    try:
        existing_vote = Vote.query.filter_by(user_id=user_id, post_id=post.id).first()

        if existing_vote:
            if existing_vote.vote_type == action:
                #cancel vote
                db.session.delete(existing_vote)
                post.post_rating += 1 if action == 'downvote' else -1
            else:
                #change vote
                existing_vote.vote_type = action
                post.post_rating += 2 if action == 'upvote' else -2
        else:
            #new vote
            new_vote = Vote(user_id=user_id, post_id=post_id, vote_type=action, action_token=action_token)
            db.session.add(new_vote)
            post.post_rating += 1 if action == 'upvote' else -1


        db.session.commit()
        return jsonify({'message': 'Post rating updated successfully!', 'rating': post.post_rating}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500






