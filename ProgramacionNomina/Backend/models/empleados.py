from ProgramacionNomina.Backend.database.app_database import leer_json, escribir_json, siguiente_id_json
 
 
class Empleado:
    """
    Representa un empleado de la empresa.
 
    Atributos:
        id              -- Identificador único autoincremental
        nombre          -- Nombre completo del empleado
        documento       -- Número de cédula o documento
        cargo           -- Cargo o puesto de trabajo
        fecha_contrato  -- Fecha de contratación (YYYY-MM-DD)
        salario_base    -- Salario base mensual en pesos colombianos
        id_grupo        -- ID del grupo al que pertenece (puede ser None)
        estado          -- 'activo' o 'inactivo'
    """
 
    def __init__(self, id, nombre, documento, cargo,
                 fecha_contrato, salario_base, id_grupo=None, estado="activo"):
        self.id             = id
        self.nombre         = nombre
        self.documento      = documento
        self.cargo          = cargo
        self.fecha_contrato = fecha_contrato
        self.salario_base   = float(salario_base)
        self.id_grupo       = id_grupo
        self.estado         = estado
 
    def objeto_a_dict(self):
        """Convierte el objeto a diccionario para guardar en JSON."""
        return {
            "id":             self.id,
            "nombre":         self.nombre,
            "documento":      self.documento,
            "cargo":          self.cargo,
            "fecha_contrato": self.fecha_contrato,
            "salario_base":   self.salario_base,
            "id_grupo":       self.id_grupo,
            "estado":         self.estado,
        }
 
    @staticmethod
    def crear_emp_desde_dict(dict_empleado):
        """Crea un objeto Empleado desde un diccionario."""
        return Empleado(
            id=dict_empleado["id"],
            nombre=dict_empleado["nombre"],
            documento=dict_empleado["documento"],
            cargo=dict_empleado["cargo"],
            fecha_contrato=dict_empleado["fecha_contrato"],
            salario_base=dict_empleado["salario_base"],
            id_grupo=dict_empleado.get("id_grupo"),
            estado=dict_empleado.get("estado", "activo"),
        )
    
    #CRUD
       
    @staticmethod
    def crear_emp(nombre, documento, cargo, fecha_contrato, salario_base, id_grupo=None):
        """
        Crea y guarda un nuevo empleado.
        Retorna el objeto Empleado creado.
        Lanza ValueError si el documento ya existe.
        """
        datos = leer_json()
 
        # Validar documento único
        for e in datos["empleados"]:
            if e["documento"] == str(documento):
                raise ValueError(f"Ya existe un empleado con el documento '{documento}'.")
 
        nuevo = Empleado(
            id=siguiente_id_json(datos["empleados"]),
            nombre=nombre.strip(),
            documento=str(documento).strip(),
            cargo=cargo.strip(),
            fecha_contrato=fecha_contrato,
            salario_base=salario_base,
            id_grupo=id_grupo,
        )
        datos["empleados"].append(nuevo.objeto_a_dict())
        escribir_json(datos)
        return nuevo
 
    @staticmethod
    def obj_desde_dict():
        """Retorna lista de objetos Empleado."""
        datos = leer_json()
        return [Empleado.crear_emp_desde_dict(e) for e in datos["empleados"]]
 
    @staticmethod
    def obtener_por_id(emp_id):
        """Retorna un Empleado por ID o None si no existe."""
        datos = leer_json()
        for e in datos["empleados"]:
            if e["id"] == int(emp_id):
                return Empleado.crear_emp_desde_dict(e)
        return None
 
    @staticmethod
    def actualizar(emp_id, nombre=None, cargo=None, salario_base=None, id_grupo=None):
        """
        Actualiza los campos indicados del empleado.
        Retorna True si se actualizó, False si no se encontró.
        """
        datos = leer_json()
        for e in datos["empleados"]:
            if e["id"] == int(emp_id):
                if nombre       is not None: e["nombre"]       = nombre.strip()
                if cargo        is not None: e["cargo"]        = cargo.strip()
                if salario_base is not None: e["salario_base"] = float(salario_base)
                if id_grupo     is not None: e["id_grupo"]     = id_grupo
                escribir_json(datos)
                return True
        return False
 
    @staticmethod
    def dar_de_baja(emp_id):
        """
        Cambia el estado a 'inactivo'.
        No borra el historial del empleado.
        """
        datos = leer_json()
        for e in datos["empleados"]:
            if e["id"] == int(emp_id):
                e["estado"] = "inactivo"
                escribir_json(datos)
                return True
        return False
    #mostrar empleado
    def __repr__(self):
        return f"<Empleado id={self.id} nombre='{self.nombre}' estado='{self.estado}'>"