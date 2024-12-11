from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from .models import User

class UserService:
    @staticmethod
    def register_user(username, password, name, age):
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            return jsonify({'error': 'Username already exists'}), 409

        new_user = User(username=username, password=password, name=name, age=age)
        new_user.save()
        return new_user