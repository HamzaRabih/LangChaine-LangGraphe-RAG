"""RAG sur le reglement interieur (PDF -> embeddings HuggingFace -> Chroma persistant).

Le reglement est indexe une fois et persiste sur disque ; il est recharge
automatiquement au demarrage (ou re-indexe depuis le PDF de documents/ si absent).
"""
import chromadb
from PyPDF2 import PdfReader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from . import config

_embedding_model = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
    return _embedding_model


def _client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=str(config.REGLEMENT_STORE_PATH))


def _extract_pdf_text(pdf_docs) -> str:
    parts = []
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                parts.append(text)
    return "\n".join(parts).strip()


def index_reglement(pdf_docs):
    """(Re)indexe le reglement et le persiste. -> (retriever, err)."""
    if not pdf_docs:
        return None, "Veuillez fournir au moins un PDF de reglement."

    content = _extract_pdf_text(pdf_docs)
    if not content:
        return None, "Aucun texte exploitable n'a ete extrait du PDF."

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=512, chunk_overlap=32,
    )
    chunks = splitter.split_text(content)
    if not chunks:
        return None, "Le texte extrait est vide apres decoupage."

    client = _client()
    try:
        client.delete_collection(config.REGLEMENT_COLLECTION_NAME)
    except Exception:
        pass

    vector_store = Chroma.from_texts(
        chunks,
        get_embedding_model(),
        collection_name=config.REGLEMENT_COLLECTION_NAME,
        client=client,
    )
    return vector_store.as_retriever(search_kwargs={"k": config.TEXT_RETRIEVAL_K}), None


def load_reglement_retriever():
    """Charge le reglement deja persiste, ou None si absent/vide."""
    if not config.REGLEMENT_STORE_PATH.exists():
        return None
    try:
        vector_store = Chroma(
            collection_name=config.REGLEMENT_COLLECTION_NAME,
            embedding_function=get_embedding_model(),
            client=_client(),
        )
        if vector_store._collection.count() == 0:
            return None
        return vector_store.as_retriever(search_kwargs={"k": config.TEXT_RETRIEVAL_K})
    except Exception:
        return None


def ensure_reglement_retriever():
    """Charge le reglement persiste ; sinon indexe le PDF de documents/.

    -> (retriever, source) avec source in {"persisted", "default", err, None}.
    """
    retriever = load_reglement_retriever()
    if retriever is not None:
        return retriever, "persisted"

    default_pdf = config.DEFAULT_REGLEMENT_PDF
    if default_pdf is not None and default_pdf.exists():
        with open(default_pdf, "rb") as f:
            retriever, err = index_reglement([f])
        return retriever, ("default" if retriever else err)

    return None, None
