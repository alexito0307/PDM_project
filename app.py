from flask import Flask
import os
from dotenv import load_dotenv
from config.db import init_db
from routes.usuarios import usuarios_bp
from routes.posts import posts_bp
from routes.comments import comments_bp
from flask_jwt_extended import JWTManager


# Loadeamos variables de entorno del .env
load_dotenv()
def create_app(): 
  # Instancia de la app
  app = Flask(__name__)
  init_db(app)
  #JWT
  app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
  jwt = JWTManager(app)
  app.register_blueprint(usuarios_bp)
  app.register_blueprint(posts_bp)
  app.register_blueprint(comments_bp)
  return app

app = create_app()

if __name__ == "__main__":
  port = int(os.getenv("PORT",8080))

  app.run(host="0.0.0.0",port=port,debug=True)