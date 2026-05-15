import os
import time
import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from ragas import evaluate, EvaluationDataset
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from rag.vectorstore import build_vector_store, get_embeddings_model


# ================================================================================
# CONFIGURACION
# ================================================================================

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

LLM_MODEL = "gemini-3.1-flash-lite-preview"
MAX_TOKENS = 2048
K_FRAGMENTOS = 5


# ================================================================================
# PROMPT AUMENTADO (MISMO QUE USA EL CHAT)
# ================================================================================

PROMPT_TEMPLATE = """Eres un Asesor Experto en Normativa de Transito Colombiano.
Tu funcion es analizar casos relacionados con comparendos, infracciones y normativa vial,
basandote EXCLUSIVAMENTE en el contexto que se te proporciona.

REGLAS IMPORTANTES:
1. Responde SOLO con la informacion del contexto. No inventes leyes ni articulos.
2. Si la respuesta no se encuentra en el contexto, responde exactamente:
   "No encuentro esa informacion en el Codigo Nacional de Transito Colombiano"
3. Si la pregunta NO es sobre transito colombiano, responde exactamente:
   "Esta consulta no esta relacionada con el ambito de transito colombiano, por lo que no puedo responderla."
4. Si el usuario pide ayuda para evadir multas, responde:
   "No puedo ayudar a evadir sanciones o incumplir la normativa de transito."
5. Si conoces el articulo aplicable, citalo textualmente al final de tu respuesta (ejemplo: ". [Artículo 122]").
6. Usa un tono profesional, claro y conversacional.
7. Responde de forma breve y directa (maximo 6 lineas).

Contexto del Codigo Nacional de Transito:
{context}

Pregunta del usuario:
{question}

Respuesta:"""


prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)


# ================================================================================
# MUESTRAS DE EVALUACION (10 PREGUNTAS)
# ================================================================================

MUESTRAS_EVALUACION = [ 
        # ----------------------------------------------------------------- # TIPO A — Recuperación directa (Texto explícito) # ----------------------------------------------------------------- 
    { 
        "user_input": "¿Qué tipos de sanciones contempla el Código Nacional de Tránsito?", 
        "reference": "Las sanciones incluyen amonestación, multa, suspensión o cancelación de la licencia, e inmovilización o retención del vehículo. [Artículo 122]", 
    }, 
    { 
        "user_input": "¿Cómo define la ley la reincidencia?", 
        "reference": "Se considera reincidencia el haber cometido más de una falta a las normas de tránsito en un periodo de seis meses. [Artículo 124]", 
    },
    # -----------------------------------------------------------------
    # TIPO B — Búsqueda semántica (Defensa técnica)
    # -----------------------------------------------------------------
    {
        "user_input": "¿Es legal que me impongan una multa si otra persona iba conduciendo mi vehículo?",
        "reference": "No, el código establece explícitamente que las multas no podrán ser impuestas a persona distinta de quien cometió la infracción. [Artículo 129]",
    },
    {
        "user_input": "¿En qué medida se calculan los montos de las multas de tránsito?",
        "reference": "Salvo disposición contraria, la multa debe entenderse establecida en salarios mínimos diarios legales vigentes. [Artículo 122]",
    },
    {
        "user_input": "Si un agente no puede ver mi licencia física, ¿puede hacerme un comparendo?",
        "reference": "Sí, pero en ese caso el funcionario deberá aportar pruebas objetivas que sustenten el informe o la infracción. [Artículo 129]",
    },

    # -----------------------------------------------------------------
    # TIPO C — Síntesis multi-chunk (Procedimiento y equipo)
    # -----------------------------------------------------------------
    {
        "user_input": "¿Qué pasa si llego a mi carro cuando una grúa lo está levantando por estar mal parqueado?",
        "reference": "Si el responsable del vehículo se hace presente en el lugar, únicamente habrá lugar a la imposición del comparendo y no se procederá al traslado a los patios. [Artículo 127]",
    },
    {
        "user_input": "¿Qué procedimiento se sigue si mi vehículo falla la prueba de gases?",
        "reference": "Se entrega una citación para inspección técnica; si se determina la infracción, el usuario tiene 15 días para reparar el vehículo y presentarlo a una nueva revisión. [Artículo 122]",
    },
    {
        "user_input": "¿Qué formalidad se debe cumplir al ingresar un vehículo a un parqueadero por inmovilización?",
        "reference": "Se debe realizar un inventario de los elementos contenidos en el vehículo y una descripción de su estado exterior tanto a la entrada como a la salida. [Artículo 125]",
    },

    # -----------------------------------------------------------------
    # TIPO D — No-alucinación / Fuera de dominio
    # -----------------------------------------------------------------
    {
        "user_input": "¿Cuál es el número de teléfono para saber dónde está mi carro inmovilizado en Bogotá?",
        "reference": "El documento menciona que debe existir un sistema de información central, pero no proporciona números telefónicos específicos para ciudades.",
    },
    {
        "user_input": "¿Cómo puedo obtener un descuento para el pago del impuesto vehicular?",
        "reference": "Esta información no se encuentra en las fuentes, ya que el documento se centra en sanciones y procedimientos de tránsito, no en impuestos.",
    },
]


# ================================================================================
# INICIALIZAR LLM, EMBEDDINGS Y BASE VECTORIAL
# ================================================================================

llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL,
    temperature=0.0,
    max_output_tokens=MAX_TOKENS,
    google_api_key=API_KEY
)

vector_store = build_vector_store([], API_KEY, force_rebuild=False)
embeddings_model = get_embeddings_model(API_KEY)


# ================================================================================
# PIPELINE RAG PARA LA EVALUACION
# ================================================================================

def rag_pipeline_eval(pregunta, k=K_FRAGMENTOS):
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )
    docs = retriever.invoke(pregunta)

    contexto = "\n\n---\n\n".join(
        f"[Fragmento {i+1} - Pag. {d.metadata.get('page','?')}]\n{d.page_content}"
        for i, d in enumerate(docs)
    )

    prompt = prompt_template.invoke({"context": contexto, "question": pregunta})
    respuesta = llm.invoke(prompt)

    if isinstance(respuesta.content, list):
        texto = respuesta.content[0].get("text", "")
    else:
        texto = respuesta.content

    return {
        "respuesta": texto.strip(),
        "fragmentos": docs,
    }


# ================================================================================
# EVALUACION POR LOTES DE 2 PREGUNTAS
# ================================================================================

def evaluar_lote(lote_muestras):
    registros = []

    for muestra in lote_muestras:
        pregunta = muestra["user_input"]
        resultado = rag_pipeline_eval(pregunta)

        registros.append({
            "user_input":         pregunta,
            "retrieved_contexts": [doc.page_content for doc in resultado["fragmentos"]],
            "response":           resultado["respuesta"],
            "reference":          muestra["reference"]
        })

        print(f"  [OK] {pregunta}")
        print(f"       -> {resultado['respuesta']}...")

    dataset = EvaluationDataset.from_list(registros)

    llm_juez = LangchainLLMWrapper(llm)
    embeddings_juez = LangchainEmbeddingsWrapper(embeddings_model)

    resultado_ragas = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=llm_juez,
        embeddings=embeddings_juez,
    )

    return resultado_ragas.to_pandas()


# ================================================================================
# EJECUCION PRINCIPAL
# ================================================================================

def ejecutar_evaluacion():
    print("=" * 70)
    print("EVALUACION DEL SISTEMA RAG - TRANSITO COLOMBIANO")
    print("=" * 70)
    print(f"Total de muestras: {len(MUESTRAS_EVALUACION)}")
    print("Evaluacion por lotes de 2 preguntas\n")

    todos_resultados = []
    total_lotes = len(MUESTRAS_EVALUACION) // 2

    for i in range(0, len(MUESTRAS_EVALUACION), 2):
        num_lote = (i // 2) + 1
        lote = MUESTRAS_EVALUACION[i:i+2]

        print(f"\n----- Lote {num_lote}/{total_lotes} -----")
        df_lote = evaluar_lote(lote)
        todos_resultados.append(df_lote)

        print(f"\nResultados del lote {num_lote}:")
        cols = ["user_input", "faithfulness", "answer_relevancy", "context_precision"]
        cols_existentes = [c for c in cols if c in df_lote.columns]
        print(df_lote[cols_existentes].to_string(index=False))

        # Pausa entre lotes para no saturar la API
        if num_lote < total_lotes:
            print("\nPausa de 5 segundos antes del siguiente lote...")
            time.sleep(5)

    # ================================================================================
    # PROMEDIOS GLOBALES
    # ================================================================================

    df_final = pd.concat(todos_resultados, ignore_index=True)

    print("\n" + "=" * 70)
    print("RESULTADOS GLOBALES")
    print("=" * 70)

    cols_score = ["faithfulness", "answer_relevancy", "context_precision"]
    cols_mostrar = ["user_input"] + [c for c in cols_score if c in df_final.columns]
    print(df_final[cols_mostrar].to_string(index=False))

    print("\nPromedios globales:")
    promedios = {}
    for col in cols_score:
        if col in df_final.columns:
            promedio = df_final[col].mean()
            promedios[col] = promedio
            print(f"  {col:<25} {promedio:.4f}")

    return df_final, promedios


if __name__ == "__main__":
    ejecutar_evaluacion()
