"""Configuration et regles RH partagees.

Ces valeurs DOIVENT rester coherentes avec le contenu du reglement interieur (PDF)
genere par generate_reglement.py : les tools de calcul s'appuient dessus, et l'agent
lit la meme regle via le RAG documentaire.
"""
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

# --- Regles de conges payes (droit francais) ---
CONGES_PAR_MOIS = 2.5      # jours ouvrables acquis par mois de travail effectif
CONGES_PLAFOND = 30        # plafond annuel (5 semaines)

# --- Prime d'anciennete : % selon le nombre d'annees revolues ---
# (on applique le pourcentage du plus haut seuil atteint)
PRIME_ANCIENNETE_SEUILS = {3: 3, 6: 6, 9: 9, 12: 12, 15: 15}  # annees -> %

# --- Conges exceptionnels (jours ouvrables) ---
CONGES_EXCEPTIONNELS = {
    "mariage": 4,
    "pacs": 4,
    "naissance": 3,
    "adoption": 3,
    "deces conjoint": 3,
    "deces enfant": 5,
    "deces parent": 3,
    "demenagement": 1,
}

# --- Roles (middleware) : instruction injectee + modele ---
ROLE_INSTRUCTIONS = {
    "employe": (
        "Tu t'adresses a un EMPLOYE. Adopte un ton bienveillant et pedagogique, "
        "explique simplement. Ne divulgue JAMAIS le salaire ni les donnees "
        "personnelles d'AUTRES employes ; limite-toi aux informations generales et "
        "au dossier de la personne qui pose la question."
    ),
    "manager": (
        "Tu t'adresses a un MANAGER RH. Donne des reponses completes et precises, "
        "cite les articles du reglement interieur, et tu peux traiter les dossiers "
        "de tous les employes (y compris l'information salariale)."
    ),
}

# --- RAG ---
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
REGLEMENT_COLLECTION_NAME = "reglement_collection"

_BASE_DIR = Path(__file__).parent

# Store vectoriel PERSISTANT (le reglement est indexe une fois puis recharge).
REGLEMENT_STORE_PATH = _BASE_DIR / "reglement-store-vdb"

# Dossier ou tu deposes le reglement interieur (PDF).
DOCUMENTS_DIR = _BASE_DIR / "documents"

# Base de donnees employes (BDD simulee).
BDD_PATH = _BASE_DIR / "data" / "employes.json"

TEXT_RETRIEVAL_K = 4


def find_default_reglement_pdf():
    """Reglement par defaut = un PDF de DOCUMENTS_DIR.

    Priorise un nom contenant 'reglement' ou 'interieur', sinon le 1er PDF.
    Renvoie un Path ou None.
    """
    if not DOCUMENTS_DIR.exists():
        return None
    pdfs = sorted(DOCUMENTS_DIR.glob("*.pdf"))
    if not pdfs:
        return None
    for pdf in pdfs:
        name = pdf.name.lower()
        if "reglement" in name or "règlement" in name or "interieur" in name:
            return pdf
    return pdfs[0]


DEFAULT_REGLEMENT_PDF = find_default_reglement_pdf()
