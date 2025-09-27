# config.py
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()  # lee .env

@dataclass
class Settings:
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "bamx")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "1") == "1"

settings = Settings()

_client: MongoClient | None = None  # singleton del cliente

def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        if not settings.MONGO_URI:
            raise RuntimeError("MONGO_URI no está configurado en .env")
        _client = MongoClient(settings.MONGO_URI, server_api=ServerApi("1"))
        _client.admin.command("ping")  # prueba rápida
    return _client

def init_db(app):
    client = get_mongo_client()
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    app.mongo_client = client
    app.db = client[settings.MONGO_DB_NAME]
    return app.db