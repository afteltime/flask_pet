from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template, session
import bcrypt
from app.models import User
from flask_wtf.csrf import generate_csrf

api_routes = Blueprint('api_routes', __name__)

class UserRegistration:
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    @staticmethod
    def validate_input(username, password):
        if not username or not password:
            return False, "username and pass are required"
        if len(password) < 6:
            return False, "password must be at least 6 char"
        return True, None

    @staticmethod
    def save_user_to_db(username, password_hash, name, age, rating=0):
        new_user = User(username=username, password_hash=password_hash.decode('utf-8'), name=name, age=age)
        new_user.save()

    @staticmethod
    @api_routes.route('/api/register', methods=['POST'])
    def register():
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        age = request.form.get('age')
        mail = request.form.get('mail')

        # bot protect (mail is hidden)
        if mail:
            return jsonify({"error": "Invalid submission"}), 400



        is_valid, error_message = UserRegistration.validate_input(username, password)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        password_hash = UserRegistration.hash_password(password)
        try:
            UserRegistration.save_user_to_db(username, password_hash, name, age)
        except Exception as e:
            if "1062" in str(e):
                return jsonify({'error': 'Username already exists'}), 409
            return jsonify({'error': str(e)}), 500

        return jsonify({'message': 'User registered successfully'}), 201


    @staticmethod
    @api_routes.route('/api/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            password_hash = User.get_password(username)
            stay_logged_in = request.form.get('stay_logged_in')
            mail = request.form.get('mail')

            #bot protect (mail is hidden)
            if mail:
               flash('invalid username or password', 'error')
               return jsonify({"error": "Invalid submission"}), 400


            if password_hash and bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                session['user'] = username
                user = User.query.filter_by(username=username).first()
                session['user_id'] = user.id
                session['role']= user.role
                if stay_logged_in:
                    session.permanent = True
                flash('Login successful!', 'success')
                return redirect(url_for('admin.admin_panel' if user.role == 'admin' else 'api.user_profile', username=username))
            else:
                flash('Invalid username or password', 'error')
                return  redirect(url_for('api.login'))
        csrf_token = generate_csrf()
        return render_template('login.html', csrf_token=csrf_token)


    @api_routes.route('/logout')
    def logout():
        session.pop('user', None)
        flash('You have been logged out', 'success')
        return redirect(url_for('api.login'))