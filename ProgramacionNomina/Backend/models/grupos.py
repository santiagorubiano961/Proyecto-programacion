from ProgramacionNomina.Backend.database.app_database import leer_json, escribir_json, siguiente_id_json
 
 
class Grupo:
    """
    Representa un grupo de trabajo dentro de la empresa.
 
    Atributos:
        id                  -- Identificador único autoincremental
        nombre              -- Nombre del grupo (ej: 'Grupo A')
        linea_grupo         -- Línea de producción o área (ej: 'Línea 1')
        programacion_grupo  -- Turno o programación (ej: 'Turno Mañana')
        integrantes         -- Lista de IDs de empleados que pertenecen al grupo
    """
 
    def __init__(self, id, nombre, linea_grupo, programacion_grupo, integrantes=None):
        self.id                 = id
        self.nombre             = nombre
        self.linea_grupo        = linea_grupo
        self.programacion_grupo = programacion_grupo
        self.integrantes        = integrantes if integrantes is not None else []
 
    # ── Conversión ──────────────────────────────────────────
 
    def a_dict(self):
        """Convierte el objeto a diccionario para guardar en JSON."""
        return {
            "id":                 self.id,
            "nombre":             self.nombre,
            "linea_grupo":        self.linea_grupo,
            "programacion_grupo": self.programacion_grupo,
            "integrantes":        self.integrantes,
        }
 
    @staticmethod
    def desde_dict(d):
        """Crea un objeto Grupo desde un diccionario."""
        return Grupo(
            id=d["id"],
            nombre=d["nombre"],
            linea_grupo=d.get("linea_grupo", ""),
            programacion_grupo=d.get("programacion_grupo", ""),
            integrantes=d.get("integrantes", []),
        )
 
    # ── Métodos CRUD ─────────────────────────────────────────
 
    @staticmethod
    def crear(nombre, linea_grupo, programacion_grupo):
        """
        Crea y guarda un nuevo grupo.
        Retorna el objeto Grupo creado.
        Lanza ValueError si ya existe un grupo con ese nombre.
        """
        datos = leer_json()
 
        # Validar nombre único
        for g in datos["grupos"]:
            if g["nombre"].lower() == nombre.strip().lower():
                raise ValueError(f"Ya existe un grupo con el nombre '{nombre}'.")
 
        nuevo = Grupo(
            id=siguiente_id_json(datos["grupos"]),
            nombre=nombre.strip(),
            linea_grupo=linea_grupo.strip(),
            programacion_grupo=programacion_grupo.strip(),
        )
        datos["grupos"].append(nuevo.a_dict())
        escribir_json(datos)
        return nuevo
 
    @staticmethod
    def obtener_todos():
        """Retorna lista de objetos Grupo."""
        datos = leer_json()
        return [Grupo.desde_dict(g) for g in datos["grupos"]]
 
    @staticmethod
    def obtener_por_id(grupo_id):
        """Retorna un Grupo por ID o None si no existe."""
        datos = leer_json()
        for g in datos["grupos"]:
            if g["id"] == int(grupo_id):
                return Grupo.desde_dict(g)
        return None
 
    @staticmethod
    def actualizar(grupo_id, nombre=None, linea_grupo=None, programacion_grupo=None):
        """
        Actualiza los campos indicados del grupo.
        Retorna True si se actualizó, False si no se encontró.
        """
        datos = leer_json()
        for g in datos["grupos"]:
            if g["id"] == int(grupo_id):
                if nombre              is not None: g["nombre"]             = nombre.strip()
                if linea_grupo         is not None: g["linea_grupo"]        = linea_grupo.strip()
                if programacion_grupo  is not None: g["programacion_grupo"] = programacion_grupo.strip()
                escribir_json(datos)
                return True
        return False
 
    def anadir_integrante(self, emp_id):
        """
        Agrega un empleado al grupo (si no está ya).
        Actualiza el campo id_grupo del empleado también.
        """
        datos = leer_json()
 
        # Actualizar grupo
        for g in datos["grupos"]:
            if g["id"] == self.id:
                if int(emp_id) not in g["integrantes"]:
                    g["integrantes"].append(int(emp_id))
                    self.integrantes = g["integrantes"]
 
        # Actualizar id_grupo del empleado
        for e in datos["empleados"]:
            if e["id"] == int(emp_id):
                e["id_grupo"] = self.id
 
        escribir_json(datos)
 
    def eliminar_integrante(self, emp_id):
        """
        Elimina un empleado del grupo.
        Limpia el campo id_grupo del empleado.
        """
        datos = leer_json()
 
        for g in datos["grupos"]:
            if g["id"] == self.id:
                g["integrantes"] = [i for i in g["integrantes"] if i != int(emp_id)]
                self.integrantes = g["integrantes"]
 
        for e in datos["empleados"]:
            if e["id"] == int(emp_id) and e.get("id_grupo") == self.id:
                e["id_grupo"] = None
 
        escribir_json(datos)
 
    @staticmethod
    def eliminar(grupo_id):
        """
        Elimina un grupo por ID.
        Retorna True si se eliminó, False si no se encontró.
        """
        datos = leer_json()
        antes = len(datos["grupos"])
        datos["grupos"] = [g for g in datos["grupos"] if g["id"] != int(grupo_id)]
        if len(datos["grupos"]) < antes:
            escribir_json(datos)
            return True
        return False
 
    def __repr__(self):
        return f"<Grupo id={self.id} nombre='{self.nombre}' integrantes={self.integrantes}>"