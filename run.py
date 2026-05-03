"""
run.py
Punto de entrada de la aplicación.
Ejecutar con: python run.py
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)