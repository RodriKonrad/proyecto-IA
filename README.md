# Tutor IA Académico - Programación

Este proyecto contiene una implementación de un tutor académico de programación con Inteligencia Artificial de Google (Gemini) usando Flask para interfaz web.

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener:
* Python 3.10 o superior
* Una **API Key** de Google AI Studio (Gemini). Puedes obtenerla en https://aistudio.google.com/

## 🚀 Configuración del Entorno

Sigue estos pasos para ejecutar el proyecto localmente:

### 1) Clonar el repositorio

```bash
git clone <tu-repo> proyecto-IA
cd proyecto-IA
```

### 2) Crear y activar el entorno virtual

En Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

En macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4) Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con tu clave:

```bash
GEMINI_API_KEY=tu_clave_secreta_aqui
```

## 💻 Uso

Ejecuta la aplicación:

```bash
python run.py
```

Abre en tu navegador: `http://127.0.0.1:5000`

## 📚 Rutas disponibles

* `/` - Interfaz del tutor IA
* `/ayuda` - Página de ayuda
* `/chat/send` - Endpoint API para enviar mensajes (POST JSON con `message`)

## 🧠 Estructura principal

* `run.py` - Arranca la app Flask.
* `app/__init__.py` - Configura la app y API key.
* `app/routes.py` - Define rutas HTML y API de chat con Gemini.
* `app/templates/` - Vistas HTML (`index.html`, `ayuda.html`).
* `app/static/` - CSS y JS (`style.css`, `script.js`).

## 🗒️ Anotaciones extra

* Si agregas dependencias nuevas, actualiza `requirements.txt` con:

```bash
pip freeze > requirements.txt
```

* Si hay problema con la API key, revisa que `.env` exista en la raíz y que la variable tenga un valor correcto.

## ✅ Ejemplo de ejecución

1. Arranca el servidor.
2. Abre `http://127.0.0.1:5000`.
3. Escribe tu pregunta de programación.
4. Presiona Enviar para recibir orientación del tutor IA.


![Tutor IA Académico](34693.png)

---
