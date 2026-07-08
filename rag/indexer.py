"""
rag/indexer.py

Construit l index FAISS a partir du schema de la base
et du mapping optionnel fourni par l utilisateur.

Usage :
    build_index()           <- construit l index
    search("ma question")   <- retourne les passages pertinents
"""

import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# ── Chemins absolus ────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BASE_DIR, "data", "schema_description.txt")
INDEX_PATH  = os.path.join(BASE_DIR, "rag",  "faiss_index.bin")
CHUNKS_PATH = os.path.join(BASE_DIR, "rag",  "chunks.pkl")
MODEL_NAME  = "all-MiniLM-L6-v2"

# ── Modele charge une seule fois en memoire ────────────────────────
_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print("Chargement du modele d embeddings...")
        _model = SentenceTransformer(MODEL_NAME)
        print("Modele charge.")
    return _model


# ══════════════════════════════════════════════════════════════════
# BUILD INDEX
# ══════════════════════════════════════════════════════════════════

def build_index(mapping_text: str = "") -> None:
    """
    Lit le schema + mapping optionnel,
    vectorise et sauvegarde l index FAISS sur disque.

    Le schema vient de data/schema_description.txt (fixe, cree par le dev).
    Le mapping vient du fichier uploade par l utilisateur (optionnel).
    """

    # 1. Lire le schema technique
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(
            f"schema_description.txt introuvable : {SCHEMA_PATH}"
        )

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()

    # 2. Decouper en blocs
    #    Chaque paragraphe vide = nouveau chunk
    chunks = []
    for block in schema.strip().split("\n\n"):
        block = block.strip()
        if block:
            chunks.append(block)

    print(f"Schema : {len(chunks)} passages extraits.")

    # 3. Ajouter le mapping utilisateur si fourni
    if mapping_text:
        mapping_chunks = []
        for line in mapping_text.strip().split("\n"):
            line = line.strip()
            if line:
                mapping_chunks.append(line)
        chunks.extend(mapping_chunks)
        print(f"Mapping : {len(mapping_chunks)} regles ajoutees.")

    print(f"Total passages a indexer : {len(chunks)}")

    # 4. Vectoriser tous les chunks
    model      = get_model()
    embeddings = model.encode(
        chunks,
        show_progress_bar=True,
        batch_size=32
    )
    embeddings = np.array(embeddings).astype("float32")

    # 5. Creer l index FAISS (distance L2)
    dimension = embeddings.shape[1]
    index     = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # 6. Sauvegarder sur disque
    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print(f"Index FAISS sauvegarde : {INDEX_PATH}")
    print(f"Chunks sauvegardes     : {CHUNKS_PATH}")


# ══════════════════════════════════════════════════════════════════
# SEARCH
# ══════════════════════════════════════════════════════════════════

def search(question: str, k: int = 3) -> list[str]:
    """
    Retourne les k passages les plus proches
    semantiquement de la question.

    Si l index n existe pas encore, le construit automatiquement.
    """

    # Auto-build si index absent
    if not os.path.exists(INDEX_PATH):
        print("Index absent. Construction automatique...")
        build_index()

    # Charger l index et les chunks
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)

    # Vectoriser la question
    model = get_model()
    q_vec = model.encode([question]).astype("float32")

    # Recherche FAISS — top k passages
    distances, indices = index.search(q_vec, k)

    # Retourner les passages correspondants
    results = []
    for idx in indices[0]:
        if 0 <= idx < len(chunks):
            results.append(chunks[idx])

    return results


# ══════════════════════════════════════════════════════════════════
# REBUILD — Reconstruit si mapping change
# ══════════════════════════════════════════════════════════════════

def rebuild_with_mapping(mapping_text: str) -> None:
    """
    Appele quand l utilisateur uploade un nouveau fichier mapping.
    Reconstruit l index en incluant les nouvelles regles.
    """
    print("Reconstruction de l index avec le mapping...")
    build_index(mapping_text=mapping_text)
    print("Index reconstruit avec succes.")


# ══════════════════════════════════════════════════════════════════
# TEST
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("=" * 55)
    print("CONSTRUCTION DE L INDEX RAG")
    print("=" * 55)
    build_index()

    print()
    print("=" * 55)
    print("TESTS DE RECHERCHE")
    print("=" * 55)

    tests = [
        "clients actifs a haut risque",
        "transactions suspectes ce mois",
        "solde moyen des comptes epargne",
        "quelle agence a le plus de comptes",
        "historique des soldes d un compte",
    ]

    for question in tests:
        print(f"\nQuestion : {question}")
        passages = search(question, k=2)
        for i, passage in enumerate(passages, 1):
            apercu = passage[:70].replace("\n", " ")
            print(f"  [{i}] {apercu}...")