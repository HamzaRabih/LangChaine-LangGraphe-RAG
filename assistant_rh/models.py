"""Les deux modeles Gemini (palier gratuit) utilises par l'agent et le middleware.

advanced_llm : gemini-2.5-flash      -> role "manager" (reponses completes/rigoureuses)
basic_llm    : gemini-2.5-flash-lite -> role "employe" (rapide, vulgarise)
"""
from langchain_google_genai import ChatGoogleGenerativeAI

from . import config  # noqa: F401  -- importe config en premier pour charger le .env

ADVANCED_MODEL = "gemini-2.5-flash"
BASIC_MODEL = "gemini-2.5-flash-lite"

advanced_llm = ChatGoogleGenerativeAI(model=ADVANCED_MODEL, temperature=0)
basic_llm = ChatGoogleGenerativeAI(model=BASIC_MODEL, temperature=0)
