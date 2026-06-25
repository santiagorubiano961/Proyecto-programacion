import sys
import os
 
# Agregar la carpeta raiz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
 
from Backend.app_backend import crear_app
 
app = crear_app()
 
if __name__ == "__main__":
    print("\n" + "="*45)
    print("  SEN - Sistema Empresarial de Nomina")
    print("="*45)
    print("  URL      : http://localhost:5000")
    print("  Usuario  : admin")
    print("  Contrasena: admin123")
    print("="*45 + "\n")
    app.run(debug=True, port=5000)