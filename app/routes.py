"""
app/routes.py
"""
import os
from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory

main = Blueprint("main", __name__)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

EVAL_RESULTS = [
    {"pregunta": "¿Qué tipos de sanciones contempla el Código Nacional de Tránsito?",       "faithfulness": 1.000000, "answer_relevancy": 0.699228, "context_precision": 1.000000},
    {"pregunta": "¿Cómo define la ley la reincidencia?",                                     "faithfulness": 0.500000, "answer_relevancy": 0.816719, "context_precision": 1.000000},
    {"pregunta": "¿Es legal que me impongan una multa si otra persona iba conduciendo mi vehículo?", "faithfulness": 1.000000, "answer_relevancy": 0.778375, "context_precision": 1.000000},
    {"pregunta": "¿En qué medida se calculan los montos de las multas de tránsito?",         "faithfulness": 0.750000, "answer_relevancy": 0.774682, "context_precision": 0.533333},
    {"pregunta": "Si un agente no puede ver mi licencia física, ¿puede hacerme un comparendo?", "faithfulness": 0.666667, "answer_relevancy": 0.798273, "context_precision": 0.500000},
    {"pregunta": "¿Qué pasa si llego a mi carro cuando una grúa lo está levantando por estar mal parqueado?",        "faithfulness": 1.000000, "answer_relevancy": 0.799504, "context_precision": 0.866667},
    {"pregunta": "¿Qué procedimiento se sigue si mi vehículo falla la prueba de gases?",     "faithfulness": 1.000000, "answer_relevancy": 0.839286, "context_precision": 0.000000},
    {"pregunta": "¿Qué formalidad se debe cumplir al ingresar un vehículo a un parqueadero por inmovilización?", "faithfulness": 1.000000, "answer_relevancy": 0.860103, "context_precision": 1.000000},
    {"pregunta": "¿Cuál es el número de teléfono para saber dónde está mi carro inmovilizado en Bogotá?", "faithfulness": 0.000000, "answer_relevancy": 0.000000, "context_precision": 0.700000},
    {"pregunta": "¿Cómo puedo obtener un descuento para el pago del impuesto vehicular?",    "faithfulness": 0.000000, "answer_relevancy": 0.000000, "context_precision": 0.500000},
]

GLOBAL_AVERAGES = {
    "faithfulness":      0.6917,
    "answer_relevancy":  0.6366,
    "context_precision": 0.7100,
}

CIRC = 314.16  # circumference for SVG gauge r=50


def _offset(value):
    return round(CIRC * (1.0 - float(value)), 2)


def _chip(value):
    v = float(value)
    if v >= 0.7:  return "green"
    if v >= 0.5:  return "amber"
    return "red"


@main.route("/")
def home():
    return render_template("index.html", active="inicio")


@main.route("/ayuda")
def ayuda():
    return render_template("ayuda.html", active="ayuda")


@main.route("/evaluacion")
def evaluacion():
    rows = [
        {
            **r,
            "off_f":  _offset(r["faithfulness"]),
            "off_a":  _offset(r["answer_relevancy"]),
            "off_c":  _offset(r["context_precision"]),
            "chip_f": _chip(r["faithfulness"]),
            "chip_a": _chip(r["answer_relevancy"]),
            "chip_c": _chip(r["context_precision"]),
        }
        for r in EVAL_RESULTS
    ]
    g = GLOBAL_AVERAGES
    return render_template(
        "evaluacion.html",
        active="evaluacion",
        resultados=rows,
        promedios=g,
        total_consultas=len(rows),
        CIRC=CIRC,
        off_faith=_offset(g["faithfulness"]),
        off_rel=_offset(g["answer_relevancy"]),
        off_prec=_offset(g["context_precision"]),
        chip_faith=_chip(g["faithfulness"]),
        chip_rel=_chip(g["answer_relevancy"]),
        chip_prec=_chip(g["context_precision"]),
    )


@main.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(ASSETS_DIR, filename)


@main.route("/chat/send", methods=["POST"])
def chat_send():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Cuerpo de la solicitud inválido o vacío."}), 400
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "El mensaje no puede estar vacío."}), 400
        rag_pipeline = current_app.config.get("RAG_PIPELINE")
        if rag_pipeline is None:
            return jsonify({"error": "El sistema RAG no está inicializado."}), 500
        answer = rag_pipeline.query(user_message)
        return jsonify({"status": "success", "response": answer}), 200
    except Exception as exc:
        print(f"[ERROR] /chat/send: {exc}")
        return jsonify({"error": str(exc)}), 500


@main.route("/chat/reset", methods=["POST"])
def chat_reset():
    rag_pipeline = current_app.config.get("RAG_PIPELINE")
    if rag_pipeline:
        rag_pipeline.clear_history()
    return jsonify({"status": "success", "message": "Historial reiniciado."}), 200
