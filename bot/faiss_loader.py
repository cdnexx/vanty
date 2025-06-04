from pathlib import Path
import pickle, faiss

BASE_DIR = Path(__file__).resolve().parent
chunks = []
index = None

def cargar_datos_vectorizados():
    global chunks, index
    try:
        with open(BASE_DIR / "models" / "vector_data" / "chunks.pkl", "rb") as f:
            chunks = pickle.load(f)
        index = faiss.read_index(str(BASE_DIR / "models" / "vector_data" / "index.faiss"))
        print("✅ FAISS y chunks cargados.")
    except FileNotFoundError:
        print("❌ Archivos FAISS o chunks no encontrados.")

cargar_datos_vectorizados()