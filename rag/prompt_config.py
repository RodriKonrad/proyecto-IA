"""
rag/prompt_config.py
Configuración del prompt del sistema, rol del asistente y formato de salida.

Este módulo centraliza toda la ingeniería de prompts del sistema RAG.
"""

from langchain_core.prompts import ChatPromptTemplate


# ─────────────────────────────────────────────────────────────────────────────
# INSTRUCCIÓN DE SISTEMA (system instruction)
# Define el ROL, las RESTRICCIONES y el COMPORTAMIENTO del asistente.
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_INSTRUCTION = """Eres un Asesor Experto en Normativa de Tránsito Colombiano.
Tu función es analizar casos relacionados con comparendos, infracciones y normativa vial,
basándote EXCLUSIVAMENTE en los documentos oficiales que te han sido proporcionados.

ROL:
- Eres un asistente técnico y objetivo, no un abogado.
- Analizas hechos, identificas normativa aplicable y das conclusiones fundamentadas.
- Tu conocimiento proviene ÚNICAMENTE de los documentos PDF del sistema.

RESTRICCIONES ABSOLUTAS:
- NUNCA inventes leyes, artículos o sanciones que no aparezcan en los documentos.
- NUNCA respondas preguntas fuera del dominio de tránsito colombiano.
- Si la información está relacionada con el área de tránsito pero no está en los documentos, responde exactamente:
  "No encontré información suficiente en los documentos disponibles para responder esta consulta."
- Si la información NO está relacionada con el área de tránsito, responde exactamente:
  "Esta consulta no está relacionada con el ámbito de tránsito colombiano, por lo que no puedo responderla."
- No des consejos ilegales ni instrucciones para evadir sanciones.
- No asumas hechos que el usuario no haya proporcionado.

COMPORTAMIENTO:
- Usa lenguaje claro, técnico y profesional.
- Cita explícitamente artículos o normas cuando estén disponibles en el contexto.
- Si la información del caso es incompleta, solicita los datos faltantes.
- Si hay versiones contradictorias entre el usuario y la autoridad, indícalo.

FORMATO OBLIGATORIO DE RESPUESTA:

**1. Resumen del caso**
Descripción objetiva de los hechos presentados.

**2. Normativa aplicable**
Normas, artículos o principios relevantes encontrados en los documentos.

**3. Análisis**
- Evaluación de si la conducta constituye una infracción.
- Inconsistencias o elementos que podrían afectar la validez del comparendo.
- Contradicciones entre versiones si las hay.

**4. Conclusión**
Determina si el comparendo:
- Parece justificado
- Podría ser cuestionable
- No es posible determinarlo con la información disponible

**5. Recomendación**
Acciones legales o administrativas válidas (apelación, solicitud de pruebas, etc.).
"""


# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE DE PROMPT AUMENTADO (RAG prompt)
# Incluye el contexto recuperado + la pregunta del usuario.
# ─────────────────────────────────────────────────────────────────────────────

RAG_PROMPT_TEMPLATE = """{system_instruction}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTEXTO RECUPERADO DE LOS DOCUMENTOS OFICIALES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HISTORIAL DE CONVERSACIÓN:
{history}

CONSULTA DEL USUARIO:
{question}

RESPUESTA DEL ASESOR:"""


def build_prompt_template() -> ChatPromptTemplate:
    """
    Construye y devuelve el ChatPromptTemplate configurado para el pipeline RAG.

    Variables del template:
        - system_instruction : instrucciones del sistema (inyectadas automáticamente)
        - context            : fragmentos recuperados del vector store
        - history            : historial de conversación (últimos turnos)
        - question           : pregunta del usuario en el turno actual

    Returns:
        ChatPromptTemplate listo para usar en la chain.
    """
    return ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)


def format_context(retrieved_docs: list) -> str:
    """
    Formatea los documentos recuperados como bloque de contexto legible.

    Args:
        retrieved_docs: lista de Document objects del retriever.

    Returns:
        String con el contexto formateado, listo para insertar en el prompt.
    """
    if not retrieved_docs:
        return "No se recuperaron fragmentos relevantes para esta consulta."

    parts = []
    for i, doc in enumerate(retrieved_docs, 1):
        import os
        fuente = os.path.basename(doc.metadata.get("source", "documento desconocido"))
        pagina = doc.metadata.get("page", "?")
        parts.append(
            f"[Fragmento {i} — Fuente: {fuente}, Página {pagina}]\n"
            f"{doc.page_content.strip()}"
        )

    return "\n\n---\n\n".join(parts)


def format_history(history: list[dict]) -> str:
    """
    Formatea el historial de conversación para incluirlo en el prompt.

    Args:
        history: lista de dicts con keys 'role' y 'content'.

    Returns:
        String del historial formateado, o 'Sin historial previo.' si está vacío.
    """
    if not history:
        return "Sin historial previo."

    lines = []
    for msg in history[-6:]:  # últimos 3 turnos (usuario + asistente)
        role = "Usuario" if msg["role"] == "user" else "Asesor"
        lines.append(f"{role}: {msg['content']}")

    return "\n".join(lines)