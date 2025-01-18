from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from .models import User, db, Post, Vote
from .decorators import login_required, role_required

admin_routes = Blueprint('admin', __name__)


@admin_routes.route('/admin')
@role_required('admin')
def admin_panel():
    return render_template('adminpanel.html')

@admin_routes.route('/admin/search', methods=['POST'])
@role_required('admin')
def search_user():
    search_query = request.form.get('search_query')
    user = User.query.filter((User.id == search_query) | (User.username == search_query)).first()
    if user:
        return redirect(url_for('admin.edit_user', id=user.id))
    return render_template('adminpanel.html', user=None)

@admin_routes.route('/admin/add', methods=['POST'])
@role_required('admin')
def add_user():
    username = request.form.get('username')
    password_hash = request.form.get('password_hash')
    name = request.form.get('name')
    age = request.form.get('age')
    rating = request.form.get('rating')
    role = request.form.get('role')

    new_user = User(username=username, password_hash=password_hash, name=name, age=age, rating=rating, role=role)
    new_user.save()
    return redirect(url_for('admin.admin_panel'))

@admin_routes.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@role_required('admin')
def edit_user(id):
    user = User.query.get(id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.password_hash = request.form.get('password_hash')
        user.name = request.form.get('name')
        user.age = request.form.get('age')
        user.rating = request.form.get('rating')
        user.role = request.form.get('role')
        new_id = request.form.get('new_id')
        if new_id:
            try:
                new_id_int = int(new_id)
                user.update_id(new_id_int)
            except ValueError:
                return "Invalid ID", 400
        db.session.commit()
        return redirect(url_for('admin.admin_panel'))
    return render_template('edit_user.html', user=user)

@admin_routes.route('/admin/delete/<int:id>', methods=['POST'])
@role_required('admin')
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.admin_panel'))

@admin_routes.route('/admin/users')
@role_required('admin')
def list_users():
    users = User.query.all()
    return render_template('list_users.html', users=users)

@admin_routes.route('/admin/feed', methods=['POST', 'GET', 'DELETE'])
@role_required('admin')
def red_posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('admin_feed.html', posts=posts)



@admin_routes.route('/admin/feed/edit/<int:post_id>', methods=['POST'])
@role_required('admin')
def edit_post(post_id):
    post = Post.query.get(post_id)
    if post:
        content = request.form['content']
        post.content = content
        db.session.commit()
        flash('Post updated successfully!', 'success')
    else:
        flash('Post not found', 'error')
    return redirect(url_for('admin.red_posts'))

@admin_routes.route('/admin/feed/delete/<int:post_id>', methods=['POST'])
@role_required('admin')
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post:
        try:
            Vote.query.filter_by(post_id=post.id).delete()
            db.session.delete(post)
            db.session.commit()
            flash('Post deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occured: {str(e)}', 'error')
    else:
        flash('Post not found', 'error')

    return redirect(url_for('admin.red_posts'))
