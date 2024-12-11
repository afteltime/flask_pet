from datetime import datetime

from . import db



class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, default=0)
    role = db.Column(db.String(50), nullable=False, default='user')
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def __init__(self, username, password_hash, name, age, rating=0, role='user'):
        self.username = username
        self.password_hash = password_hash
        self.name = name
        self.age = age
        self.rating = rating
        self.role = role

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update_id(self, new_id):
        self.id = new_id
        db.session.commit()

    @staticmethod
    def get_all_users():
        return User.query.all()


    @staticmethod
    def get_password(username):
        user = User.query.filter_by(username=username).first()
        if user:
            return user.password_hash
        return None



class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_rating = db.Column(db.Integer, default=0)



    def __repr__(self):
        return f'<Post {self.content}>'