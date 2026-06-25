import json
import os

_RUTA = os.path.join(os.path.dirname(__file__), "trabajadores.json")

#leer jason
def leer_json():
    with open(_RUTA, "r", encoding="utf8") as f:
        return json.load(f)

#escribir jason
def escribir_json(datos):
    with open(_RUTA, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

#escribir jason
def siguiente_id_json(lista):
    if not lista:
        return 1
    return max(item["id"] for item in lista) + 1