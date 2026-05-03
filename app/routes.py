"""
app/routes.py
Rutas de la aplicación Flask.
El endpoint /chat/send usa el pipeline RAG para responder consultas.
"""

from flask import Blueprint, render_template, request, jsonify, current_app

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html", title="Inicio")


@main.route("/ayuda")
def ayuda():
    return render_template("ayuda.html", title="Ayuda")


@main.route("/chat/send", methods=["POST"])
def chat_send():
    """
    Endpoint principal de consulta.
    Recibe la pregunta del usuario y devuelve la respuesta del pipeline RAG.

    Request body (JSON):
        { "message": "texto de la consulta" }

    Response (JSON):
        { "status": "success", "response": "respuesta del asesor" }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Cuerpo de la solicitud inválido o vacío."}), 400

        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "El mensaje no puede estar vacío."}), 400

        # Obtener el pipeline RAG inicializado en create_app()
        rag_pipeline = current_app.config.get("RAG_PIPELINE")
        if rag_pipeline is None:
            return jsonify({"error": "El sistema RAG no está inicializado."}), 500

        # Ejecutar el pipeline (recuperación + generación)
        # Los fragmentos recuperados se imprimen automáticamente en consola (debug)
        answer = rag_pipeline.query(user_message)

        return jsonify({"status": "success", "response": answer}), 200

    except Exception as exc:
        print(f"[ERROR] /chat/send: {exc}")
        return jsonify({"error": str(exc)}), 500


@main.route("/chat/reset", methods=["POST"])
def chat_reset():
    """Reinicia el historial de conversación del pipeline RAG."""
    rag_pipeline = current_app.config.get("RAG_PIPELINE")
    if rag_pipeline:
        rag_pipeline.clear_history()
    return jsonify({"status": "success", "message": "Historial reiniciado."}), 200