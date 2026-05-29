import json
import os
from Backend.models.empleados import Empleado
ruta_json  = 'Backend/database/trabajadores.json'

def crear_nuevo_grupo(numero_grupo,lista_nombres):
    if os.path.exists(ruta_json):
        with open(ruta_json, 'r', encoding= 'utf-8') as archivo:
            try:
                datos_actuales