from flask import Blueprint, current_app, request, jsonify
from bson import ObjectId
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity

from dotenv import load_dotenv

import datetime

comments_bp = Blueprint('comments', __name__, url_prefix='/comments') 

# Comentar posts
@comments_bp.route('/<post_id>/comment', methods=['POST'])
@jwt_required()
def comment_post(post_id):
    username = get_jwt_identity()
    
    getData = request.get_json()
    comment_text = getData.get('comment')

    if not comment_text:
        return {'error': 'El comentario no puede estar vacío'}, 400

    post = current_app.db.posts.find_one({'_id': ObjectId(post_id)})
    if not post:
        return {'error': 'Post no encontrado'}, 404

    comment = {
        'username': username,
        'comment': comment_text,
        'created_at': datetime.datetime.utcnow(),
        '_id': str(ObjectId())
        
    }

    if not isinstance(comment_text, str):
        return {'error': 'El comentario debe ser una cadena de texto'}, 400

    current_app.db.posts.update_one(
        {'_id': ObjectId(post_id)},
        {'$push': {'comments': comment}}
    )
    return {'message': 'Comentario agregado exitosamente'}, 201

# Obtener comentarios de un post
@comments_bp.route('/<post_id>/comments', methods=['GET'])
def get_comments(post_id):
    post = current_app.db.posts.find_one({'_id': ObjectId(post_id)})
    if not post:
        return {'error': 'Post no encontrado'}, 404
    comments = post.get('comments', [])
    return {'comments': comments}, 200

# Borrar un comentario de un post
@comments_bp.route('/<post_id>/comment/<comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(post_id, comment_id):
    username = get_jwt_identity()

    post = current_app.db.posts.find_one({'_id': ObjectId(post_id)})
    if not post:
        return {'error': 'Post no encontrado'}, 404

    comment = next((c for c in post.get('comments', []) if c['_id'] == comment_id), None)
    if not comment:
        return {'error': 'Comentario no encontrado'}, 404

    if comment['username'] != username:
        return {'error': 'No tienes permiso para eliminar este comentario'}, 403

    current_app.db.posts.update_one(
        {'_id': ObjectId(post_id)},
        {'$pull': {'comments': {'_id': comment_id}}}
    )
    return {'message': 'Comentario eliminado exitosamente'}, 200