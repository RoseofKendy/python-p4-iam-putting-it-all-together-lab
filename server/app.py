from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, Recipe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key'

CORS(app, supports_credentials=True)

db.init_app(app)
migrate = Migrate(app, db)

### SESSION ROUTES ###

@app.post('/signup')
def signup():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    image_url = data.get('image_url')
    bio = data.get('bio')

    if not username or not password:
        return {"error": "Username and password are required."}, 422

    try:
        new_user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )
        new_user.password_hash = password
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id

        return jsonify({
            "id": new_user.id,
            "username": new_user.username,
            "image_url": new_user.image_url,
            "bio": new_user.bio
        }), 201

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 422


@app.get('/check_session')
def check_session():
    user_id = session.get('user_id')
    if not user_id:
        return {"error": "Unauthorized"}, 401

    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 401

    return {
        "id": user.id,
        "username": user.username,
        "image_url": user.image_url,
        "bio": user.bio
    }


@app.post('/login')
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.authenticate(password):
        session['user_id'] = user.id
        return {
            "id": user.id,
            "username": user.username,
            "image_url": user.image_url,
            "bio": user.bio
        }

    return {"error": "Unauthorized"}, 401


@app.delete('/logout')
def logout():
    if not session.get('user_id'):
        return {"error": "Unauthorized"}, 401

    session['user_id'] = None
    return {}, 204


### RECIPE ROUTES ###

@app.get('/recipes')
def get_recipes():
    user_id = session.get('user_id')
    if not user_id:
        return {"error": "Unauthorized"}, 401

    user = User.query.get(user_id)
    recipes = Recipe.query.filter_by(user_id=user.id).all()

    return [{
        "id": recipe.id,
        "title": recipe.title,
        "instructions": recipe.instructions,
        "minutes_to_complete": recipe.minutes_to_complete
    } for recipe in recipes], 200


@app.post('/recipes')
def create_recipe():
    user_id = session.get('user_id')
    if not user_id:
        return {"error": "Unauthorized"}, 401

    data = request.get_json()

    try:
        new_recipe = Recipe(
            title=data.get('title'),
            instructions=data.get('instructions'),
            minutes_to_complete=data.get('minutes_to_complete'),
            user_id=user_id
        )

        db.session.add(new_recipe)
        db.session.commit()

        return {
            "id": new_recipe.id,
            "title": new_recipe.title,
            "instructions": new_recipe.instructions,
            "minutes_to_complete": new_recipe.minutes_to_complete
        }, 201

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 422


if __name__ == '__main__':
    app.run(debug=True)
