from pathlib import Path
import pickle, faiss

BASE_DIR = Path(__file__).resolve().parent
chunks_info = []
index_info = None

chunks_scripts = []
index_scripts = None


def cargar_datos_vectorizados():
    global chunks_info, index_info, chunks_scripts, index_scripts
    try:
        with open(BASE_DIR / "models" / "vector_data" / "info" / "chunks.pkl", "rb") as f:
            chunks_info = pickle.load(f)
        index_info = faiss.read_index(str(BASE_DIR / "models" / "vector_data" / "info" / "index.faiss"))
        print("✅ FAISS y chunks cargados para INFO.")
    except FileNotFoundError:
        print("❌ Archivos FAISS o chunks no encontrados para INFO.")
    try:
        with open(BASE_DIR / "models" / "vector_data" / "scripts" / "chunks.pkl", "rb") as f:
            chunks_scripts = pickle.load(f)
        index_scripts = faiss.read_index(str(BASE_DIR / "models" / "vector_data" / "scripts" / "index.faiss"))
        print("✅ FAISS y chunks cargados para SCRIPTS.")
    except FileNotFoundError:
        print("❌ Archivos FAISS o chunks no encontrados para SCRIPTS.")

cargar_datos_vectorizados()