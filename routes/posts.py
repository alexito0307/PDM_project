from flask import Blueprint, current_app, request, jsonify
from bson import ObjectId
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity

from dotenv import load_dotenv

import datetime

# Obtenemos las variables de entorno
load_dotenv()

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')

# Obtener todos los posts
@posts_bp.route('/', methods=['GET'])
def get_posts():
    posts = list(current_app.db.posts.find())
    for post in posts:
        post['_id'] = str(post['_id'])
    return {'posts': posts}, 200

# Obterner un post por su ID
@posts_bp.route('/<post_id>', methods=['GET'])
def get_post(post_id):
    post = current_app.db.posts.find_one({'_id': ObjectId(post_id)})
    if not post:
        return {'error': 'Post no encontrado'}, 404
    post['_id'] = str(post['_id'])  
    return post, 200

# Crear posts
@posts_bp.route('/', methods=['POST'])
@jwt_required()
def create_post():
    getData = request.get_json()
    title = getData.get('title')
    description = getData.get('description')
    img_url = getData.get('img_url')

    username = get_jwt_identity()

    if not title:
        return {'error': 'Faltan datos obligatorios'}, 400

    new_post = {
        'title': title,
        'description': description,
        'img_url': img_url,
        'username': username,
        'likes': 0,
        'liked_by': [],
        'created_at': datetime.datetime.utcnow(),
        'comments': []
    }
    current_app.db.posts.insert_one(new_post)
    return {'message': 'Post creado exitosamente'}, 201

# Update posts
@posts_bp.route('/<post_id>', methods=['PATCH'])
@jwt_required()
def update_post(post_id):
    username = get_jwt_identity()
    
    getData = request.get_json()
    title = getData.get('title')
    description = getData.get('description')


    if not title or not description:
        return {'error': 'Faltan datos obligatorios'}, 400
    
    post = current_app.db.posts.find_one({'_id': ObjectId(post_id)})
    if not post:
        return {'error': 'Post no encontrado'}, 404

    # Verificar que el dueño sea el mismo que está logueado
    if post['username'] != username:
        return {'error': 'No tienes permiso para editar este post'}, 403

    updated_post = {
        'title': title,
        'description': description
    }
    current_app.db.posts.update_one({'_id': ObjectId(post_id)}, {'$set': updated_post})
    return {'message': 'Post actualizado exitosamente'}, 200

# Borrar posts
@posts_bp.route('/<post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    username = get_jwt_identity()

    post = current_app.db.posts.find_one({'_id': ObjectId(post_id)})
    if not post:
        return {'error': 'Post no encontrado'}, 404

    if post['username'] != username:
        return {'error': 'No tienes permiso para eliminar este post'}, 403

    current_app.db.posts.delete_one({'_id': ObjectId(post_id)})
    return {'message': 'Post eliminado exitosamente'}, 200

# Like posts
@posts_bp.route('/<post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    username = get_jwt_identity()

    post = current_app.db.posts.find_one({'_id': ObjectId(post_id)})
    if not post:
        return {'error': 'Post no encontrado'}, 404

    if username in post.get('liked_by', []):
        return {'error': 'Ya has dado like a este post'}, 400

    current_app.db.posts.update_one(
        {'_id': ObjectId(post_id)},
        {
            '$inc': {'likes': 1},
            '$push': {'liked_by': username}
        }
    )
    return {'message': 'Has dado like al post'}, 200

# Unlikear posts
@posts_bp.route('/<post_id>/unlike', methods=['POST'])
@jwt_required()
def unlike_post(post_id):
    username = get_jwt_identity()

    post = current_app.db.posts.find_one({'_id': ObjectId(post_id)})
    if not post:
        return {'error': 'Post no encontrado'}, 404

    if username not in post.get('liked_by', []):
        return {'error': 'No has dado like a este post'}, 400

    current_app.db.posts.update_one(
        {'_id': ObjectId(post_id)},
        {
            '$inc': {'likes': -1},
            '$pull': {'liked_by': username}
        }
    )
    return {'message': 'Has quitado el like al post'}, 200