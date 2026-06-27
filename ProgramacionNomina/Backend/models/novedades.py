from Backend.database.app_database import leer_json, escribir_json, siguiente_id_json


class Novedad:
    """
    Representa una novedad laboral de un empleado en un periodo.

    Atributos:
        id              -- ID autoincremental
        id_empleado     -- ID del empleado al que aplica
        periodo         -- Periodo en formato YYYY-MM (ej: 2026-06)
        tipo            -- 'horas_extras' | 'incapacidad' | 'vacaciones' | 'permiso'
        descripcion     -- Descripción libre de la novedad
        extra_diurnas       -- Horas extras diurnas (recargo 25%)
        extra_nocturnas     -- Horas extras nocturnas (recargo 75%)
        recargos_nocturnos  -- Horas con recargo nocturno (recargo 35%)
        recargos_festivos   -- Horas festivas diurnas (recargo 75%)
        recargos_fest_noct  -- Horas festivas nocturnas (recargo 110%)
        horas_dom_diurnas   -- Horas dominicales diurnas (recargo 75%)
        horas_dom_nocturnas -- Horas dominicales nocturnas (recargo 110%)
        dias_incapacidad    -- Días de incapacidad médica
        dias_vacaciones     -- Días de vacaciones
        dias_permiso        -- Días de permiso no remunerado
    """

    def __init__(self, id, id_empleado, periodo, tipo="horas_extras",
                 descripcion="",
                 extra_diurnas=0, extra_nocturnas=0,
                 recargos_nocturnos=0, recargos_festivos=0, recargos_fest_noct=0,
                 horas_dom_diurnas=0, horas_dom_nocturnas=0,
                 dias_incapacidad=0, dias_vacaciones=0, dias_permiso=0):

        self.id                  = id
        self.id_empleado         = id_empleado
        self.periodo             = periodo
        self.tipo                = tipo
        self.descripcion         = descripcion
        self.extra_diurnas       = float(extra_diurnas)
        self.extra_nocturnas     = float(extra_nocturnas)
        self.recargos_nocturnos  = float(recargos_nocturnos)
        self.recargos_festivos   = float(recargos_festivos)
        self.recargos_fest_noct  = float(recargos_fest_noct)
        self.horas_dom_diurnas   = float(horas_dom_diurnas)
        self.horas_dom_nocturnas = float(horas_dom_nocturnas)
        self.dias_incapacidad    = float(dias_incapacidad)
        self.dias_vacaciones     = float(dias_vacaciones)
        self.dias_permiso        = float(dias_permiso)

    # ── Conversión ───────────────────────────────────────────

    def objeto_a_dict(self):
        return {
            "id":                  self.id,
            "id_empleado":         self.id_empleado,
            "periodo":             self.periodo,
            "tipo":                self.tipo,
            "descripcion":         self.descripcion,
            "extra_diurnas":       self.extra_diurnas,
            "extra_nocturnas":     self.extra_nocturnas,
            "recargos_nocturnos":  self.recargos_nocturnos,
            "recargos_festivos":   self.recargos_festivos,
            "recargos_fest_noct":  self.recargos_fest_noct,
            "horas_dom_diurnas":   self.horas_dom_diurnas,
            "horas_dom_nocturnas": self.horas_dom_nocturnas,
            "dias_incapacidad":    self.dias_incapacidad,
            "dias_vacaciones":     self.dias_vacaciones,
            "dias_permiso":        self.dias_permiso,
        }

    @staticmethod
    def crear_novedad_desde_dict(d):
        return Novedad(
            id=d["id"],
            id_empleado=d["id_empleado"],
            periodo=d["periodo"],
            tipo=d.get("tipo", "horas_extras"),
            descripcion=d.get("descripcion", ""),
            extra_diurnas=d.get("extra_diurnas", 0),
            extra_nocturnas=d.get("extra_nocturnas", 0),
            recargos_nocturnos=d.get("recargos_nocturnos", 0),
            recargos_festivos=d.get("recargos_festivos", 0),
            recargos_fest_noct=d.get("recargos_fest_noct", 0),
            horas_dom_diurnas=d.get("horas_dom_diurnas", 0),
            horas_dom_nocturnas=d.get("horas_dom_nocturnas", 0),
            dias_incapacidad=d.get("dias_incapacidad", 0),
            dias_vacaciones=d.get("dias_vacaciones", 0),
            dias_permiso=d.get("dias_permiso", 0),
        )

    # ── CRUD ────────────────────────────────────────────────

    @staticmethod
    def crear_novedad(id_empleado, periodo, tipo, descripcion,
                      extra_diurnas, extra_nocturnas,
                      recargos_nocturnos, recargos_festivos, recargos_fest_noct,
                      horas_dom_diurnas, horas_dom_nocturnas,
                      dias_incapacidad, dias_vacaciones, dias_permiso):
        """Crea y guarda una novedad. Retorna el objeto creado."""
        datos = leer_json()
        nueva = Novedad(
            id=siguiente_id_json(datos.get("novedades", [])),
            id_empleado=int(id_empleado),
            periodo=periodo,
            tipo=tipo,
            descripcion=descripcion,
            extra_diurnas=extra_diurnas,
            extra_nocturnas=extra_nocturnas,
            recargos_nocturnos=recargos_nocturnos,
            recargos_festivos=recargos_festivos,
            recargos_fest_noct=recargos_fest_noct,
            horas_dom_diurnas=horas_dom_diurnas,
            horas_dom_nocturnas=horas_dom_nocturnas,
            dias_incapacidad=dias_incapacidad,
            dias_vacaciones=dias_vacaciones,
            dias_permiso=dias_permiso,
        )
        datos.setdefault("novedades", []).append(nueva.objeto_a_dict())
        escribir_json(datos)
        return nueva

    @staticmethod
    def obtener_todas():
        """Retorna lista de todas las novedades."""
        datos = leer_json()
        return [Novedad.crear_novedad_desde_dict(n) for n in datos.get("novedades", [])]

    @staticmethod
    def obtener_por_empleado(id_empleado):
        """Retorna novedades de un empleado específico."""
        datos = leer_json()
        return [Novedad.crear_novedad_desde_dict(n)
                for n in datos.get("novedades", [])
                if n["id_empleado"] == int(id_empleado)]

    @staticmethod
    def obtener_por_periodo(periodo):
        """Retorna novedades de un periodo específico."""
        datos = leer_json()
        return [Novedad.crear_novedad_desde_dict(n)
                for n in datos.get("novedades", [])
                if n["periodo"] == periodo]

    @staticmethod
    def obtener_por_empleado_y_periodo(id_empleado, periodo):
        """Retorna novedades de un empleado en un periodo."""
        datos = leer_json()
        return [Novedad.crear_novedad_desde_dict(n)
                for n in datos.get("novedades", [])
                if n["id_empleado"] == int(id_empleado) and n["periodo"] == periodo]

    @staticmethod
    def eliminar(novedad_id):
        """Elimina una novedad por ID."""
        datos = leer_json()
        antes = len(datos.get("novedades", []))
        datos["novedades"] = [n for n in datos.get("novedades", [])
                              if n["id"] != int(novedad_id)]
        if len(datos["novedades"]) < antes:
            escribir_json(datos)
            return True
        return False
    

    def __repr__(self):
        return f"<Novedad id={self.id} emp={self.id_empleado} periodo={self.periodo} tipo={self.tipo}>"