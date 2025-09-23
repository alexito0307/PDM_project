from flask import Blueprint, current_app
from bson import ObjectId

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

@usuarios_bp.get("")
def get_all_usuarios():
    cur = current_app.db.usuarios.find({}, {"password": 0})
    out = []
    for d in cur:
        d["_id"] = str(d["_id"])
        out.append(d)
    return out

@usuarios_bp.get("/<int:id_usuario>")
def obtener_por_id_usuario(id_usuario: int):
    doc = current_app.db.usuarios.find_one(
        {"id_usuario": id_usuario},
        {"password": 0}  # no exponer passwords
    )
    if not doc:
        return {"error": "no encontrado"}, 404

    doc["_id"] = str(doc["_id"])
    return doc

# opcional: obtener por ObjectId de Mongo
@usuarios_bp.get("/by_oid/<oid>")
def obtener_por_oid(oid: str):
    try:
        oid = ObjectId(oid)
    except Exception:
        return {"error": "id invalido"}, 400

    doc = current_app.db.usuarios.find_one({"_id": oid}, {"password": 0})
    if not doc:
        return {"error": "no encontrado"}, 404

    doc["_id"] = str(doc["_id"])
    return doc
