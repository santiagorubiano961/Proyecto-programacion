"""
SEN - Motor de Cálculo de Nómina
Aplica la legislación laboral colombiana vigente 2026.
"""

from datetime import datetime
from Backend.database.app_database import leer_json, escribir_json, siguiente_id_json
from Backend.models.novedades import Novedad


# ── PARÁMETROS LEGALES 2026 ─────────────────────────────────
SALARIO_MINIMO     = 1_423_500
AUXILIO_TRANSPORTE = 200_000

# Porcentajes empleado
SALUD_EMPLEADO    = 0.04
PENSION_EMPLEADO  = 0.04

# Porcentajes empleador
SALUD_EMPLEADOR   = 0.085
PENSION_EMPLEADOR = 0.12
ARL               = 0.00522

# Recargos sobre valor hora
RECARGO_EXTRA_DIURNA      = 0.25   # +25% sobre hora ordinaria
RECARGO_EXTRA_NOCTURNA    = 0.75   # +75%
RECARGO_NOCTURNO          = 0.35   # +35%
RECARGO_FESTIVO_DIURNO    = 0.75   # +75%
RECARGO_FESTIVO_NOCTURNO  = 1.10   # +110%
RECARGO_DOM_DIURNO        = 0.75   # +75%
RECARGO_DOM_NOCTURNO      = 1.10   # +110%

HORAS_MES = 240   # 30 días x 8 horas


def calcular_valor_hora(salario_base):
    """Retorna el valor de una hora ordinaria."""
    return salario_base / HORAS_MES


def calcular_empleado(empleado, novedades_periodo, dias_trabajados=30):
    """
    Calcula la nómina completa de un empleado para un periodo.

    Args:
        empleado        -- Objeto Empleado
        novedades_periodo -- Lista de objetos Novedad del empleado en el periodo
        dias_trabajados -- Días laborados en el mes (por defecto 30)

    Returns:
        dict con todos los conceptos devengados, deducciones y neto.
    """
    salario      = float(empleado.salario_base)
    valor_dia    = salario / 30
    valor_hora   = calcular_valor_hora(salario)

    # ── ACUMULAR NOVEDADES ──────────────────────────────────
    extra_diurnas       = sum(n.extra_diurnas       for n in novedades_periodo)
    extra_nocturnas     = sum(n.extra_nocturnas     for n in novedades_periodo)
    recargos_nocturnos  = sum(n.recargos_nocturnos  for n in novedades_periodo)
    recargos_festivos   = sum(n.recargos_festivos   for n in novedades_periodo)
    recargos_fest_noct  = sum(n.recargos_fest_noct  for n in novedades_periodo)
    horas_dom_diurnas   = sum(n.horas_dom_diurnas   for n in novedades_periodo)
    horas_dom_nocturnas = sum(n.horas_dom_nocturnas for n in novedades_periodo)
    dias_incapacidad    = sum(n.dias_incapacidad    for n in novedades_periodo)
    dias_vacaciones     = sum(n.dias_vacaciones     for n in novedades_periodo)
    dias_permiso        = sum(n.dias_permiso        for n in novedades_periodo)

    # Ajustar días trabajados por ausencias sin pago
    dias_efectivos = max(0, dias_trabajados - dias_permiso)

    # ── DEVENGADOS ──────────────────────────────────────────

    # Salario proporcional a días trabajados
    salario_periodo = valor_dia * dias_efectivos

    # Auxilio de transporte (solo si salario <= 2 SMLV)
    aux_transporte = AUXILIO_TRANSPORTE if salario <= (SALARIO_MINIMO * 2) else 0

    # Horas extras y recargos
    val_extra_diurna      = valor_hora * (1 + RECARGO_EXTRA_DIURNA)    * extra_diurnas
    val_extra_nocturna    = valor_hora * (1 + RECARGO_EXTRA_NOCTURNA)  * extra_nocturnas
    val_recargo_nocturno  = valor_hora * RECARGO_NOCTURNO              * recargos_nocturnos
    val_recargo_festivo   = valor_hora * RECARGO_FESTIVO_DIURNO        * recargos_festivos
    val_recargo_fest_noct = valor_hora * RECARGO_FESTIVO_NOCTURNO      * recargos_fest_noct
    val_dom_diurno        = valor_hora * RECARGO_DOM_DIURNO            * horas_dom_diurnas
    val_dom_nocturno      = valor_hora * RECARGO_DOM_NOCTURNO          * horas_dom_nocturnas

    # Incapacidad: 66.67% del salario diario
    val_incapacidad = valor_dia * 0.6667 * dias_incapacidad

    # Vacaciones: 50% del salario diario
    val_vacaciones = valor_dia * 0.5 * dias_vacaciones

    total_devengado = (
        salario_periodo
        + aux_transporte
        + val_extra_diurna
        + val_extra_nocturna
        + val_recargo_nocturno
        + val_recargo_festivo
        + val_recargo_fest_noct
        + val_dom_diurno
        + val_dom_nocturno
        + val_incapacidad
        + val_vacaciones
    )

    # ── DEDUCCIONES ─────────────────────────────────────────
    desc_salud   = salario * SALUD_EMPLEADO
    desc_pension = salario * PENSION_EMPLEADO
    total_deducciones = desc_salud + desc_pension

    # ── NETO ────────────────────────────────────────────────
    neto = total_devengado - total_deducciones

    return {
        "id_empleado":         empleado.id,
        "nombre":              empleado.nombre,
        "documento":           empleado.documento,
        "cargo":               empleado.cargo,
        "salario_base":        round(salario, 2),
        "dias_trabajados":     dias_efectivos,
        # Devengados
        "salario_periodo":     round(salario_periodo, 2),
        "aux_transporte":      round(aux_transporte, 2),
        "val_extra_diurna":    round(val_extra_diurna, 2),
        "val_extra_nocturna":  round(val_extra_nocturna, 2),
        "val_recargo_nocturno":round(val_recargo_nocturno, 2),
        "val_recargo_festivo": round(val_recargo_festivo, 2),
        "val_recargo_fest_noct":round(val_recargo_fest_noct, 2),
        "val_dom_diurno":      round(val_dom_diurno, 2),
        "val_dom_nocturno":    round(val_dom_nocturno, 2),
        "val_incapacidad":     round(val_incapacidad, 2),
        "val_vacaciones":      round(val_vacaciones, 2),
        "total_devengado":     round(total_devengado, 2),
        # Deducciones
        "desc_salud":          round(desc_salud, 2),
        "desc_pension":        round(desc_pension, 2),
        "total_deducciones":   round(total_deducciones, 2),
        # Neto
        "neto":                round(neto, 2),
        # Horas y días para mostrar en desprendible
        "extra_diurnas":       extra_diurnas,
        "extra_nocturnas":     extra_nocturnas,
        "dias_incapacidad":    dias_incapacidad,
        "dias_vacaciones":     dias_vacaciones,
        "dias_permiso":        dias_permiso,
    }


def calcular_nomina_periodo(periodo):
    """
    Calcula la nómina de TODOS los empleados activos para un periodo (YYYY-MM).
    Guarda el resultado en nominas del JSON.
    Retorna (lista_resultados, id_nomina).
    """
    from Backend.models.empleados import Empleado

    datos     = leer_json()
    activos   = [e for e in datos["empleados"] if e["estado"] == "activo"]
    novedades = Novedad.obtener_por_periodo(periodo)

    # Mapa de novedades por empleado
    nov_por_emp = {}
    for n in novedades:
        nov_por_emp.setdefault(n.id_empleado, []).append(n)

    resultados = []
    for emp_dict in activos:
        from Backend.models.empleados import Empleado
        emp = Empleado.crear_emp_desde_dict(emp_dict)
        nov_emp = nov_por_emp.get(emp.id, [])
        resultado = calcular_empleado(emp, nov_emp)
        resultado["periodo"] = periodo
        resultados.append(resultado)

    # Guardar nómina en histórico
    nomina = {
        "id":                siguiente_id_json(datos.get("nominas", [])),
        "periodo":           periodo,
        "fecha_liquidacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_empleados":   len(resultados),
        "total_neto":        round(sum(r["neto"] for r in resultados), 2),
        "detalle":           resultados,
    }
    datos.setdefault("nominas", []).append(nomina)
    escribir_json(datos)

    return resultados, nomina["id"]


def obtener_nominas():
    """Retorna el histórico de todas las nóminas."""
    datos = leer_json()
    return datos.get("nominas", [])


def obtener_nomina_por_id(nomina_id):
    """Retorna una nómina por ID."""
    for n in obtener_nominas():
        if n["id"] == int(nomina_id):
            return n
    return None