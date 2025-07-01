from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.Text)

    # Relationships
    recipes = db.relationship('Recipe', back_populates='user', lazy=True, cascade='all, delete-orphan')

    # Password property
    @property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password)

    def authenticate(self, password):
        return check_password_hash(self._password_hash, password)

    # Validations
    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username must be provided.")
        return username


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', back_populates='recipes')
    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions or len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions

    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title must be provided.")
        return title
