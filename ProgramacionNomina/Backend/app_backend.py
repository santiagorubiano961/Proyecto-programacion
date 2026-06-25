import os
from flask import Flask
from Backend.routes.app_routes import bp
 
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
 
def crear_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(ROOT_DIR, "Frontend", "templates"),
        static_folder=os.path.join(ROOT_DIR, "Frontend", "static")
    )
    app.secret_key = "sen_clave_secreta_2026"
    app.register_blueprint(bp)
    return app