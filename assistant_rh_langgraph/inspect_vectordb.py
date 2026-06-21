"""Inspecteur de la base vectorielle du reglement (debug).

Usage :
    uv run python assistant_rh_langgraph/inspect_vectordb.py --samples 3 --dims 8
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import chromadb

from assistant_rh_langgraph import config


def _preview_vector(vec, dims: int) -> str:
    if vec is None:
        return "—"
    head = ", ".join(f"{x:+.3f}" for x in vec[:dims])
    return f"dim={len(vec)} [{head}{', ...' if len(vec) > dims else ''}]"


def main():
    parser = argparse.ArgumentParser(description="Inspecte la base vectorielle du reglement.")
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--dims", type=int, default=8)
    args = parser.parse_args()

    path = config.REGLEMENT_STORE_PATH
    print("=" * 78)
    print("REGLEMENT INTERIEUR (texte, embeddings HuggingFace MiniLM)")
    print(f"  chemin     : {path}")
    print(f"  collection : {config.REGLEMENT_COLLECTION_NAME}")
    print("=" * 78)

    if not path.exists():
        print("  (store inexistant — rien n'a encore ete indexe)")
        return

    client = chromadb.PersistentClient(path=str(path))
    try:
        collection = client.get_collection(config.REGLEMENT_COLLECTION_NAME)
    except Exception as exc:
        print(f"  collection introuvable : {exc}")
        return

    print(f"  nombre de chunks : {collection.count()}")
    data = collection.get(limit=args.samples, include=["documents", "embeddings"])

    def _col(name):
        value = data.get(name)
        return value if value is not None else []

    ids, docs, embs = _col("ids"), _col("documents"), _col("embeddings")
    for i, _id in enumerate(ids):
        print(f"\n  [{i}] id={_id}")
        if i < len(docs) and docs[i]:
            snippet = docs[i].replace("\n", " ")[:160]
            print(f"      document : {snippet}{'...' if len(docs[i]) > 160 else ''}")
        emb = embs[i] if i < len(embs) else None
        print(f"      embedding: {_preview_vector(emb, args.dims)}")
    print()


if __name__ == "__main__":
    main()
