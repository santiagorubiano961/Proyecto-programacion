from flask import Blueprint, render_template, request, redirect, url_for, session

from Backend.database.app_database import leer_json
from Backend.models.empleados import Empleado
from Backend.models.grupos import Grupo

bp = Blueprint("rutas", __name__)


def login_requerido(f):
    """Decorador que protege rutas que requieren sesión activa."""
    from functools import wraps
    @wraps(f)
    def verificar(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("rutas.login"))
        return f(*args, **kwargs)
    return verificar


# ── LOGIN ──────────────────────────────────────────────────

@bp.route("/", methods=["GET"])
def index():
    return redirect(url_for("rutas.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario    = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "").strip()
        datos = leer_json()
        for u in datos["usuarios"]:
            if u["usuario"] == usuario and u["contrasena"] == contrasena:
                session["usuario"] = u["usuario"]
                session["rol"]     = u["rol"]
                return redirect(url_for("rutas.dashboard"))
        error = "Usuario o contraseña incorrectos."
    return render_template("index.html", error=error)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("rutas.login"))


# ── DASHBOARD ──────────────────────────────────────────────

@bp.route("/dashboard")
@login_requerido
def dashboard():
    empleados = Empleado.obtener_todos()
    grupos    = Grupo.obtener_todos()
    return render_template("dashboard.html",
                           usuario=session["usuario"],
                           rol=session["rol"],
                           total_empleados=len([e for e in empleados if e.estado == "activo"]),
                           total_grupos=len(grupos))


# ── EMPLEADOS ──────────────────────────────────────────────

@bp.route("/empleados/crear", methods=["GET", "POST"])
@login_requerido
def crear_empleado():
    error = None
    exito = None
    grupos = Grupo.obtener_todos()

    if request.method == "POST":
        try:
            id_grupo = request.form.get("id_grupo") or None
            if id_grupo:
                id_grupo = int(id_grupo)

            Empleado.crear_emp(
                nombre        = request.form.get("nombre"),
                documento     = request.form.get("documento"),
                cargo         = request.form.get("cargo"),
                fecha_contrato= request.form.get("fecha_contrato"),
                salario_base  = request.form.get("salario_base"),
                id_grupo      = id_grupo
            )
            exito = f"Empleado '{request.form.get('nombre')}' creado exitosamente."
        except ValueError as e:
            error = str(e)

    return render_template("crear_empleado.html",
                           grupos=grupos,
                           error=error,
                           exito=exito)


# ── GRUPOS ─────────────────────────────────────────────────

@bp.route("/grupos/crear", methods=["GET", "POST"])
@login_requerido
def crear_grupo():
    error = None
    exito = None

    if request.method == "POST":
        try:
            Grupo.crear_grupo(
                nombre             = request.form.get("nombre"),
                linea_grupo        = request.form.get("linea_grupo"),
                programacion_grupo = request.form.get("programacion_grupo")
            )
            exito = f"Grupo '{request.form.get('nombre')}' creado exitosamente."
        except ValueError as e:
            error = str(e)

    return render_template("crear_grupo.html", error=error, exito=exito)


# ── LISTAS (placeholder por ahora) ─────────────────────────

@bp.route("/empleados")
@login_requerido
def lista_empleados():
    empleados = Empleado.obtener_todos()
    return render_template("lista_empleados.html", empleados=empleados)


@bp.route("/grupos")
@login_requerido
def lista_grupos():
    grupos = Grupo.obtener_todos()
    return render_template("lista_grupos.html", grupos=grupos)