"""
SEN - Sistema Empresarial de Nomina Automatizada
Modulo: Backend Principal
Descripcion: Inicializa la aplicacion Flask y registra los blueprints.
"""

from flask import Flask
from Backend.routes.app_routes import bp
import os
import secrets


def crear_app():
    """Factory de la aplicacion Flask."""
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "../Frontend/templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "../Frontend/static")
    )

    # Clave secreta para sesiones (en produccion usar variable de entorno)
    app.secret_key = os.environ.get("SEN_SECRET_KEY", secrets.token_hex(24))

    # Registrar rutas
    app.register_blueprint(bp)

    return app