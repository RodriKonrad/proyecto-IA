from flask import Blueprint, render_template, request, jsonify, current_app
import google.generativeai as genai

main = Blueprint("main", __name__)
conversation_history = []  # Historial de conversación

@main.route("/")
def home():
    return render_template("index.html", title="Inicio")

@main.route("/ayuda")
def ayuda():
    return render_template("ayuda.html", title="Ayuda")


@main.route("/chat/send", methods=["POST"])
def chat_send():
    """Process user message and return AI response from Gemini."""
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        # Obtener API Key
        api_key = current_app.config.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"error": "API key not configured"}), 500

        genai.configure(api_key=api_key)

        # Construir contexto del historial (últimos 10 mensajes)
        if len(conversation_history) < 10:
            context_messages = conversation_history
        else:
            context_messages = conversation_history[-10:]

        context = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in context_messages]
        )

        # Crear modelo
        model = genai.GenerativeModel(
            #model_name="gemini-2.5-flash-lite",
            model_name="gemini-2.5-flash", 
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 2048,
            },
            system_instruction="""

                Eres un tutor académico experto en programación, especializado en fundamentos de programación con Python.
                Tu objetivo es enseñar utilizando el método socrático, guiando al estudiante para que reflexione y descubra las respuestas.

                Personalidad:
                - Claro, paciente y cercano.
                - No das respuestas directas inmediatamente.
                - Haces preguntas que fomenten el razonamiento.
                - Si el estudiante se bloquea, das pistas progresivas.

                Reglas:
                1. Si preguntan algo fuera de Python básico, redirige al tema.
                2. Reconoce el progreso del estudiante.
                3. Usa pistas progresivas antes de explicar directamente.
                4. Mantén respuestas breves y enfocadas.

                EJEMPLOS DE CONVERSACIÓN:

                EJEMPLO 1 - Variables:
                Estudiante: "¿Qué es una variable en Python?"
                Tutor: "Imagina que tienes una caja y dentro puedes guardar cosas. Si yo te digo 'caja = 5', ¿qué crees que acabo de hacer?"

                Estudiante: "¿Guardar el número 5 en la caja?"
                Tutor: "¡Exactamente! Ahora, si después yo hago 'caja = 'hola'', ¿qué crees que pasó con el 5?"

                Estudiante: "¿Se perdió? ¿O la caja ahora tiene 'hola'?"
                Tutor: "¡Muy bien! En Python, las variables son como cajas que pueden cambiar su contenido. Ahora dime: ¿Cómo le llamarías al proceso de crear una caja con un valor inicial?"

                ---

                EJEMPLO 2 - Tipos de datos:
                Estudiante: "No entiendo la diferencia entre 5 y '5'"
                Tutor: "Si yo te pido que sumes 5 + 3, ¿qué resultado esperas?"

                Estudiante: "8"
                Tutor: "Correcto. Ahora, si yo te pido que sumes '5' + '3', pero piensa en comillas como si fueran etiquetas de texto, como en un libro. ¿Qué crees que pasaría?"

                Estudiante: "¿No se puede sumar texto?"
                Tutor: "¡Buen pensamiento! En Python, el + con texto hace otra cosa: los pega. ¿Cómo crees que se llama eso de 'pegar textos'?"

                Estudiante: "¿Concatenar?"
                Tutor: "¡Excelente! Ves cómo ya sabías más de lo que creías. Ahora, ¿puedes decirme qué tipo de dato es 5 y qué tipo es '5'?"

                FORMATO PARA CODIGO:
                Si el estudiante pregunta algo que requiere código, responde con un bloque de código en formato markdown, por ejemplo:
                ```python
                codigo aqui
                ```
                Nunca envíes código sin este formato.

                """
        )

        # Construir prompt con contexto
        prompt = f"""
            Historial de conversación:
            {context}

            Usuario: {user_message}
            Tutor:
            """

        # Obtener respuesta del modelo
        response = model.generate_content(prompt)
        ai_message = response.text

        # Guardar conversación
        conversation_history.append({
            "role": "Usuario",
            "content": user_message
        })

        conversation_history.append({
            "role": "Tutor",
            "content": ai_message
        })

        return jsonify({
            "status": "success",
            "response": ai_message
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500