from sentence_transformers import SentenceTransformer, models
from llama_cpp import Llama
import numpy as np
import time
from .faiss_loader import index_info, chunks_info, index_scripts, chunks_scripts
from pathlib import Path
from datetime import datetime
from .prompts.system import SYSTEM_PROMPT
from .prompts.flujo import FLUJO_PROMPT
from .prompts.base import BASE_PROMPT
from .prompts.info import INFO_PROMPT
from .prompts.scripts import SCRIPTS_PROMPT

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
EMBEDDING_MODEL_INFO = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
EMBEDDING_MODEL_SCRIPTS = "microsoft/codebert-base"

embedder_info = SentenceTransformer(EMBEDDING_MODEL_INFO)

word_embedding_model = models.Transformer(EMBEDDING_MODEL_SCRIPTS)
pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
embedder_scripts = SentenceTransformer(modules=[word_embedding_model, pooling_model])

llama_model = Llama(
    model_path=str(MODEL_PATH),
    n_gpu_layers=-1,
    n_ctx=16384,
    n_threads=8
)

def generar_respuesta(prompt, max_tokens=512, temperature=0.5, top_k=40, top_p=0.9, min_p=0.05, repeat_penalty=1.1):
    respuesta = llama_model(
        prompt, 
        max_tokens=max_tokens,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        min_p=min_p,
        repeat_penalty=repeat_penalty
    )
    return respuesta['choices'][0]['text'].strip()
    

# k = Número de fragmentos a recuperar del índice FAISS
def buscar_contexto(pregunta, index, chunks, embedder, k=5):
    if index is None:
        return ""
    pregunta_emb = embedder.encode([pregunta])
    distances, indices = index.search(np.array(pregunta_emb), k)
    seleccionados = [chunks[i] for i in indices[0] if i < len(chunks)]
    return "\n".join(seleccionados)

def determinar_flujo(history):
    ultimo_mensaje = history[-1]
    flujo = "base" # Flujo por defecto

    prompt = f"""
            <|begin_of_text|>
            <|start_header_id|>system<|end_header_id|>
                {FLUJO_PROMPT.strip()}
            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Determina el flujo de la siguiente consulta: "{ultimo_mensaje.content.strip()}"
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>"""

    if ultimo_mensaje.message_type == 'user':
        respuesta_flujo = generar_respuesta(prompt, max_tokens=8)
        if respuesta_flujo in ['script', 'info', 'base']:
            flujo = respuesta_flujo

    return flujo

def construir_historial_info(history):
    output_prompt = ""
    # Iterar sobre el historial de mensajes, la última iteración es diferente
    for i in range(len(history)):
        message = history[i]
        message_type = 'user' if message.message_type == 'user' else 'assistant'

        if i == len(history)-1:
            if message.message_type == 'user':
                contexto = buscar_contexto(message.content, index_info, chunks_info, embedder_info)
                output_prompt += f"""
                    <|start_header_id|>{message_type}<|end_header_id|>
                    En base a la siguiente información, responde la consulta:
                    ---
                    {contexto.strip() if contexto else "No hay contexto disponible."}
                    ---
                    Consulta: {message.content.strip()}
                    <|eot_id|>"""
        else:
            output_prompt += f"""
                <|start_header_id|>{message_type}<|end_header_id|>
                    {message.content.strip()}
                <|eot_id|>"""
    return output_prompt.strip()

def construir_historial_script(history):
    output_prompt = ""
    # Iterar sobre el historial de mensajes, la última iteración es diferente
    for i in range(len(history)):
        message = history[i]
        message_type = 'user' if message.message_type == 'user' else 'assistant'

        if i == len(history)-1:
            if message.message_type == 'user':
                contexto = buscar_contexto(message.content, index_scripts, chunks_scripts, embedder_scripts)
                output_prompt += f"""
                    <|start_header_id|>{message_type}<|end_header_id|>
                    En base a la siguiente información, responde la consulta:
                    ---
                    {contexto.strip() if contexto else "No hay contexto disponible."}
                    ---
                    Consulta: {message.content.strip()}
                    <|eot_id|>"""
        else:
            output_prompt += f"""
                <|start_header_id|>{message_type}<|end_header_id|>
                    {message.content.strip()}
                <|eot_id|>"""
    return output_prompt.strip()

def construir_historial_base(history):
    output_prompt = ""
    # Iterar sobre el historial de mensajes, la última iteración es diferente
    for i in range(len(history)):
        message = history[i]
        message_type = 'user' if message.message_type == 'user' else 'assistant'
        output_prompt += f"""
            <|start_header_id|>{message_type}<|end_header_id|>
                {message.content.strip()}
            <|eot_id|>"""
    return output_prompt.strip()

def get_prompt(specific_prompt, historial, construir_historial):
    prompt = f"""
            <|begin_of_text|>
            <|start_header_id|>system<|end_header_id|>
                Location: Chile
                Today Date: {datetime.now().strftime('%A %d %B %Y')}
                Developer: Franco Osorio
                {SYSTEM_PROMPT.strip()}
                -------------------------
                {specific_prompt.strip()}
            <|eot_id|>
            {construir_historial(historial)}
            <|start_header_id|>assistant<|end_header_id|>"""
    print(prompt)
    return prompt

def flujo_base(historial):
    prompt = get_prompt(BASE_PROMPT, historial, construir_historial_base)
    return generar_respuesta(prompt, max_tokens=512)

def flujo_script(historial):
    prompt = get_prompt(SCRIPTS_PROMPT, historial, construir_historial_script)
    return generar_respuesta(prompt, max_tokens=512)

def flujo_info(historial):
    prompt = get_prompt(INFO_PROMPT, historial, construir_historial_info)
    return generar_respuesta(prompt, max_tokens=512)

def responder(historial):
    flujo = determinar_flujo(historial)
    print(f"Flujo determinado: {flujo}")
    if flujo == "script":
        respuesta = flujo_script(historial)
    elif flujo == "info":
        respuesta = flujo_info(historial)
    else:
        respuesta = flujo_base(historial)

    print(f"Respuestas:{respuesta}\n")
    return respuesta
