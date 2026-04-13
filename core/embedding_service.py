from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

def build_embedder():
    return SentenceTransformer(MODEL_NAME)

def generate_embeddings(model, texts):
    return model.encode(texts, show_progress_bar=False)
