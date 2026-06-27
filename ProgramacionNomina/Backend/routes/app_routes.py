from flask import Blueprint, render_template, request, redirect, url_for, session

from Backend.database.app_database import leer_json
from Backend.models.empleados import Empleado
from Backend.models.grupos import Grupo

bp = Blueprint("rutas", __name__)


def login_requerido(f):
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


# ── EMPLEADOS CRUD ─────────────────────────────────────────

@bp.route("/empleados")
@login_requerido
def lista_empleados():
    empleados = Empleado.obtener_todos()
    mensaje   = request.args.get("mensaje")
    return render_template("lista_empleados.html", empleados=empleados, mensaje=mensaje)


@bp.route("/empleados/crear", methods=["GET", "POST"])
@login_requerido
def crear_empleado():
    error  = None
    exito  = None
    grupos = Grupo.obtener_todos()

    if request.method == "POST":
        try:
            id_grupo = request.form.get("id_grupo") or None
            if id_grupo:
                id_grupo = int(id_grupo)
            Empleado.crear_emp(
                nombre         = request.form.get("nombre"),
                documento      = request.form.get("documento"),
                cargo          = request.form.get("cargo"),
                fecha_contrato = request.form.get("fecha_contrato"),
                salario_base   = request.form.get("salario_base"),
                id_grupo       = id_grupo
            )
            return redirect(url_for("rutas.lista_empleados",
                                    mensaje=f"Empleado '{request.form.get('nombre')}' creado exitosamente."))
        except ValueError as e:
            error = str(e)

    return render_template("crear_empleado.html", grupos=grupos, error=error, exito=exito)


@bp.route("/empleados/editar/<int:emp_id>", methods=["GET", "POST"])
@login_requerido
def editar_empleado(emp_id):
    empleado = Empleado.obtener_por_id(emp_id)
    grupos   = Grupo.obtener_todos()

    if not empleado:
        return redirect(url_for("rutas.lista_empleados", mensaje="Empleado no encontrado."))

    if request.method == "POST":
        id_grupo = request.form.get("id_grupo") or None
        if id_grupo:
            id_grupo = int(id_grupo)
        Empleado.actualizar(
            emp_id,
            nombre       = request.form.get("nombre"),
            cargo        = request.form.get("cargo"),
            salario_base = request.form.get("salario_base"),
            id_grupo     = id_grupo
        )
        return redirect(url_for("rutas.lista_empleados",
                                mensaje=f"Empleado '{request.form.get('nombre')}' actualizado."))

    return render_template("editar_empleado.html", empleado=empleado, grupos=grupos)


@bp.route("/empleados/baja/<int:emp_id>")
@login_requerido
def baja_empleado(emp_id):
    empleado = Empleado.obtener_por_id(emp_id)
    if empleado:
        Empleado.dar_de_baja(emp_id)
        return redirect(url_for("rutas.lista_empleados",
                                mensaje=f"'{empleado.nombre}' dado de baja."))
    return redirect(url_for("rutas.lista_empleados"))


@bp.route("/empleados/reactivar/<int:emp_id>")
@login_requerido
def reactivar_empleado(emp_id):
    empleado = Empleado.obtener_por_id(emp_id)
    if empleado:
        Empleado.actualizar(emp_id, nombre=empleado.nombre)
        from Backend.database.app_database import leer_json, escribir_json
        datos = leer_json()
        for e in datos["empleados"]:
            if e["id"] == emp_id:
                e["estado"] = "activo"
                break
        escribir_json(datos)
        return redirect(url_for("rutas.lista_empleados",
                                mensaje=f"'{empleado.nombre}' reactivado."))
    return redirect(url_for("rutas.lista_empleados"))


# ── GRUPOS CRUD ────────────────────────────────────────────

@bp.route("/grupos")
@login_requerido
def lista_grupos():
    grupos  = Grupo.obtener_todos()
    mensaje = request.args.get("mensaje")
    return render_template("lista_grupos.html", grupos=grupos, mensaje=mensaje)


@bp.route("/grupos/crear", methods=["GET", "POST"])
@login_requerido
def crear_grupo():
    error = None
    if request.method == "POST":
        try:
            Grupo.crear_grupo(
                nombre             = request.form.get("nombre"),
                linea_grupo        = request.form.get("linea_grupo"),
                programacion_grupo = request.form.get("programacion_grupo")
            )
            return redirect(url_for("rutas.lista_grupos",
                                    mensaje=f"Grupo '{request.form.get('nombre')}' creado exitosamente."))
        except ValueError as e:
            error = str(e)
    return render_template("crear_grupo.html", error=error)


@bp.route("/grupos/editar/<int:grupo_id>", methods=["GET", "POST"])
@login_requerido
def editar_grupo(grupo_id):
    # 1. Obtener el grupo actual
    grupo = Grupo.obtener_por_id(grupo_id)
    if not grupo:
        return "Grupo no encontrado", 404
        
    if request.method == "POST":
        # Capturar los datos básicos
        nombre = request.form.get("nombre")
        linea_grupo = request.form.get("linea_grupo")
        programacion_grupo = request.form.get("programacion_grupo")
        
        # Actualizar datos del grupo
        Grupo.actualizar(grupo_id, nombre=nombre, linea_grupo=linea_grupo, programacion_grupo=programacion_grupo)
        
        # 2. LÓGICA DE MIEMBROS: Obtener IDs seleccionados
        # getlist obtiene todos los valores con el mismo nombre 'miembros'
        id_empleados_seleccionados = [int(x) for x in request.form.getlist("miembros")]
        
        # 3. Sincronizar empleados
        todos_empleados = Empleado.obtener_todos()
        for emp in todos_empleados:
            if emp.id in id_empleados_seleccionados:
                # Si el empleado está en la lista de seleccionados, asignarle este grupo
                Empleado.actualizar(emp.id, id_grupo=grupo_id)
            elif emp.id_grupo == grupo_id:
                # Si NO está seleccionado pero ANTES pertenecía al grupo, quitarlo
                Empleado.actualizar(emp.id, id_grupo=None)
    if request.method == "POST":
        # ... (código anterior)
        
        # AGREGA ESTA LÍNEA AQUÍ:
        print("--- DEBUG ---")
        print("Lista recibida del formulario:", request.form.getlist("miembros"))
        
        # ... (resto de tu código)
                    
        return redirect(url_for("rutas.lista_grupos"))
            
    # Método GET: enviar el grupo y la lista de todos los empleados para el formulario
    empleados = Empleado.obtener_todos()
    return render_template("editar_grupo.html", grupo=grupo, empleados=empleados)


@bp.route("/grupos/eliminar/<int:grupo_id>")
@login_requerido
def eliminar_grupo(grupo_id):
    grupo = Grupo.obtener_por_id(grupo_id)
    if grupo:
        Grupo.eliminar(grupo_id)
        return redirect(url_for("rutas.lista_grupos",
                                mensaje=f"Grupo '{grupo.nombre}' eliminado."))
    return redirect(url_for("rutas.lista_grupos"))


# ── NOVEDADES ──────────────────────────────────────────────

from Backend.models.novedades import Novedad
from Backend.services.nomina  import calcular_nomina_periodo, obtener_nominas, obtener_nomina_por_id


@bp.route("/novedades")
@login_requerido
def lista_novedades():
    novedades = Novedad.obtener_todas()
    empleados = Empleado.obtener_todos()
    emp_map   = {e.id: e.nombre for e in empleados}
    mensaje   = request.args.get("mensaje")
    return render_template("lista_novedades.html",
                           novedades=novedades,
                           emp_map=emp_map,
                           mensaje=mensaje)


@bp.route("/novedades/crear", methods=["GET", "POST"])
@login_requerido
def crear_novedad():
    error     = None
    empleados = Empleado.obtener_todos()
    grupos    = Grupo.obtener_todos()

    if request.method == "POST":
        try:
            Novedad.crear_novedad(
                id_empleado         = request.form.get("id_empleado"),
                periodo             = request.form.get("periodo"),
                tipo                = request.form.get("tipo"),
                descripcion         = request.form.get("descripcion", ""),
                extra_diurnas       = request.form.get("extra_diurnas", 0),
                extra_nocturnas     = request.form.get("extra_nocturnas", 0),
                recargos_nocturnos  = request.form.get("recargos_nocturnos", 0),
                recargos_festivos   = request.form.get("recargos_festivos", 0),
                recargos_fest_noct  = request.form.get("recargos_fest_noct", 0),
                horas_dom_diurnas   = request.form.get("horas_dom_diurnas", 0),
                horas_dom_nocturnas = request.form.get("horas_dom_nocturnas", 0),
                dias_incapacidad    = request.form.get("dias_incapacidad", 0),
                dias_vacaciones     = request.form.get("dias_vacaciones", 0),
                dias_permiso        = request.form.get("dias_permiso", 0),
            )
            return redirect(url_for("rutas.lista_novedades",
                                    mensaje="Novedad registrada exitosamente."))
        except Exception as e:
            error = str(e)

    return render_template("crear_novedad.html",
                           empleados=empleados,
                           grupos=grupos,
                           error=error)


@bp.route("/novedades/eliminar/<int:nov_id>")
@login_requerido
def eliminar_novedad(nov_id):
    Novedad.eliminar(nov_id)
    return redirect(url_for("rutas.lista_novedades", mensaje="Novedad eliminada."))


# ── NÓMINA ─────────────────────────────────────────────────

@bp.route("/nomina", methods=["GET", "POST"])
@login_requerido
def nomina():
    resultado  = None
    nomina_id  = None
    error      = None
    nominas    = obtener_nominas()
    from datetime import datetime
    periodo_actual = datetime.now().strftime("%Y-%m")

    if request.method == "POST":
        periodo = request.form.get("periodo", periodo_actual)
        empleados_activos = [e for e in Empleado.obtener_todos() if e.estado == "activo"]
        if not empleados_activos:
            error = "No hay empleados activos para liquidar."
        else:
            resultado, nomina_id = calcular_nomina_periodo(periodo)
            nominas = obtener_nominas()

    return render_template("nomina.html",
                           resultado=resultado,
                           nomina_id=nomina_id,
                           nominas=nominas,
                           periodo_actual=periodo_actual,
                           error=error)