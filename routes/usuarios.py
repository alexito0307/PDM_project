from flask import Blueprint, current_app, request, jsonify
from bson import ObjectId
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
import datetime

from dotenv import load_dotenv

# Obtenemos las variables de entorno
load_dotenv()

# Inicializamos Bcrypt
bcrypt = Bcrypt()

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

# Obtener todos los usuarios
@usuarios_bp.route('/', methods=['GET'])
def get_usuarios():
    usuarios = list(current_app.db.usuarios.find())
    for usuario in usuarios:
        usuario['_id'] = str(usuario['_id'])  # Convertir ObjectId a string
    return {'usuarios': usuarios}, 200

# Crear una nueva cuenta de usuario
@usuarios_bp.route('/createAccount', methods=['POST'])
def create_account():
    # Obtener datos del request
    getData = request.get_json()
    username = getData.get('username')
    email = getData.get('email')
    password = getData.get('password')

    # Validaciones básicas
    if not username or not email or not password:
        return jsonify({'error': 'Faltan datos obligatorios'}), 400
    if current_app.db.usuarios.find_one({'email': email}):
        return jsonify({'error': 'El correo ya está en uso'}), 400
    if current_app.db.usuarios.find_one({'username': username}):
        return jsonify({'error': 'El nombre de usuario ya está en uso'}), 400
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Crear nuevo usuario
    new_user = {
        'username': username,
        'email': email,
        'password': hashed_password,
    }
    try:
        current_app.db.usuarios.insert_one(new_user)
        return jsonify({'message': 'Cuenta creada exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': f"Error en registro de usuario {str(e)}"}), 500

# Login de usuario
@usuarios_bp.route('/login', methods=['POST'])
def login():
    getData = request.get_json()
    
    email = getData.get('email')
    password = getData.get('password')

    if not email or not password:
        return jsonify({'error': 'Faltan datos obligatorios'}), 400
    usuario = current_app.db.usuarios.find_one({'email': email})
    if not usuario:
        return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

    if not bcrypt.check_password_hash(usuario['password'], password):
        return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

    usuario['_id'] = str(usuario['_id'])  # Convertir ObjectId a string

    expires = datetime.timedelta(minutes=120)
    access_token = create_access_token(
        identity=str(usuario['username']),
        additional_claims={"_id": usuario['_id']},
        expires_delta=expires
    )
    return jsonify({'message': 'Login exitoso', 'usuario': usuario, 'access_token': access_token}), 200

# Obtener un usuario por su username
@usuarios_bp.route('/<username>', methods=['GET'])
def get_usuario(username):
    usuario = current_app.db.usuarios.find_one({'username': username}, {'password': 0})
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    usuario['_id'] = str(usuario['_id']) 
    user_posts = list(current_app.db.posts.find({'username': username}))
    for post in user_posts:
        post['_id'] = str(post['_id'])  # Convertir ObjectId a string
    return jsonify({'usuario': usuario, 'posts': user_posts}), 200

# Quien soy
@usuarios_bp.route('/me', methods=['GET'])
@jwt_required()
def who_am_i():
    current_user = get_jwt_identity()
    usuario = current_app.db.usuarios.find_one({'username': current_user}, {'password': 0})
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

# Borrar usuario y sus posts
@usuarios_bp.route('/<username>', methods=['DELETE'])
@jwt_required()
def delete_user(username):
    current_user = get_jwt_identity()
    if current_user != username:
        return jsonify({'error': 'No tienes permiso para eliminar este usuario'}), 403

    usuario = current_app.db.usuarios.find_one({'username': username})
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    current_app.db.posts.delete_many({'username': username})
    current_app.db.usuarios.delete_one({'username': username})
    return jsonify({'message': 'Usuario y sus posts eliminados exitosamente'}), 200