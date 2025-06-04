from sentence_transformers import SentenceTransformer
from llama_cpp import Llama
import numpy as np
import time
from .faiss_loader import index, chunks
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "mistral-7b-instruct-v0.2.Q4_K_M.gguf"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LLAMA_MODEL_PATH = "./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

MASTER_PROMPT = """
Tu nombre es Vanty, y eres un asistente de IA diseñado para ayudar a los usuarios a interactuar con un escáner ultrasónico Vantage 32 LE.

Responde siempre en español y solo en español.  Mantén un tono profesional y amigable.

Cuando entregues scripts, comandos o código, **formatea SIEMPRE usando bloques de código con triple backtick (```), y especifica el lenguaje si es posible**, por ejemplo: ```matlab

Nunca entregues código como texto plano.

Si no tienes suficiente información, indica que no puedes ayudar con esa pregunta.

Responde en base al contexto proporcionado y al historial de conversación de forma concisa e intenta ser breve. No repitas el contexto ni el historial en tus respuestas y nunca inventes información.

"""

embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
llama_model = Llama(
    model_path=str(MODEL_PATH),
    n_gpu_layers=-1,
    n_ctx=4096,
    n_threads=8
)

def buscar_contexto(pregunta, k=5):
    if index is None:
        return ""
    pregunta_emb = embedder.encode([pregunta])
    distances, indices = index.search(np.array(pregunta_emb), k)
    seleccionados = [chunks[i] for i in indices[0] if i < len(chunks)]
    return "\n".join(seleccionados)

def responder(pregunta, history):
    historial_formateado = ""
    for user_msg, bot_msg in history:
        historial_formateado += f"[INST] {user_msg.strip()} [/INST]\n{bot_msg.strip()}\n"
    historial_formateado += f"[INST] {pregunta.strip()} [/INST]"

    contexto = buscar_contexto(pregunta)
    prompt = f"<s>[INST] {MASTER_PROMPT} [/INST]\n{historial_formateado}\n\nContexto:\n{contexto}\n\nRespuesta:"

    respuesta = llama_model(prompt, max_tokens=512)
    return respuesta['choices'][0]['text'].strip()
