from flask import Flask
import os
from dotenv import load_dotenv
from config.db import init_db
from routes.usuarios import usuarios_bp


# Loadeamos variables de entorno del .env
load_dotenv()
def create_app(): 
  # Instancia de la app
  app = Flask(__name__)
  init_db(app)
  app.register_blueprint(usuarios_bp)
  return app

app = create_app()

if __name__ == "__main__":
  port = int(os.getenv("PORT",8080))

  app.run(host="0.0.0.0",port=port,debug=True)
