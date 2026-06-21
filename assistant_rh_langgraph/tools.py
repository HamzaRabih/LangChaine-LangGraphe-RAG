"""Tools de l'assistant RH.

- RAG documentaire    : search_article
- BDD employes        : get_employe, list_employes
- Calculs (fiables)   : calc_anciennete, calc_conges, solde_conges,
                        calc_prime_anciennete, conges_exceptionnels

Les calculs sont DETERMINISTES (code Python), pas confies au LLM : l'agent lit la
regle via le RAG puis delegue le calcul au tool.
"""
import math
from datetime import date

from langchain.tools import tool

from . import config, database

# Retriever injecte par l'application apres indexation du reglement.
_reglement_retriever = None


def set_reglement_retriever(retriever) -> None:
    global _reglement_retriever
    _reglement_retriever = retriever


def _parse_date(value: str) -> date:
    """Accepte 'JJ/MM/AAAA' (ou 'aujourd'hui'/'today' -> date du jour)."""
    if value is None or str(value).strip().lower() in ("", "aujourd'hui", "today", "now"):
        return date.today()
    day, month, year = str(value).strip().split("/")
    return date(int(year), int(month), int(day))


# --------------------------------------------------------------------------- #
# RAG
# --------------------------------------------------------------------------- #
@tool
def search_article(query: str) -> str:
    """Recherche une regle dans le reglement interieur de l'entreprise.

    A utiliser pour toute question 'que dit le reglement sur ...' (teletravail,
    conges, preavis, periode d'essai, etc.).

    Args:
        query: la question ou le mot-cle a rechercher.
    Returns:
        Les passages les plus pertinents du reglement.
    """
    if _reglement_retriever is None:
        return "Reglement non disponible : aucun PDF n'a ete indexe."
    docs = _reglement_retriever.invoke(query)
    passages = "\n\n".join(d.page_content for d in docs if d.page_content)
    return passages or "Aucun passage pertinent trouve dans le reglement."


# --------------------------------------------------------------------------- #
# BDD employes
# --------------------------------------------------------------------------- #
@tool
def get_employe(nom: str) -> dict:
    """Recupere la fiche d'un employe dans la base RH.

    Args:
        nom: nom (ou prenom) de l'employe, ex: "Hamza", "Sara El Amrani".
    Returns:
        La fiche employe (matricule, departement, poste, date d'embauche, conges
        pris, salaire, statut) ou un message d'erreur si introuvable.
    """
    emp = database.find_employe(nom)
    if emp is None:
        noms = [e["nom"] for e in database.get_all()]
        return {"erreur": f"Employe '{nom}' introuvable.", "employes_connus": noms}
    return emp


@tool
def list_employes() -> list:
    """Liste les employes de la base (nom, departement, poste)."""
    return [
        {"nom": e["nom"], "departement": e["departement"], "poste": e["poste"]}
        for e in database.get_all()
    ]


# --------------------------------------------------------------------------- #
# Calculs RH (deterministes)
# --------------------------------------------------------------------------- #
@tool
def calc_anciennete(date_embauche: str, date_reference: str = "aujourd'hui") -> dict:
    """Calcule l'anciennete a partir de la date d'embauche.

    Args:
        date_embauche: date au format JJ/MM/AAAA (ex: "15/03/2021").
        date_reference: date de calcul (defaut: aujourd'hui), format JJ/MM/AAAA.
    Returns:
        dict avec annees, mois, total_mois.
    """
    emb = _parse_date(date_embauche)
    ref = _parse_date(date_reference)
    years = ref.year - emb.year
    months = ref.month - emb.month
    if ref.day < emb.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    return {
        "date_embauche": date_embauche,
        "date_reference": ref.strftime("%d/%m/%Y"),
        "annees": years,
        "mois": months,
        "total_mois": years * 12 + months,
    }


@tool
def calc_conges(mois_travailles: float) -> dict:
    """Calcule les conges payes acquis selon le droit francais.

    Regle : 2,5 jours ouvrables par mois travaille, plafonnes a 30 jours (5 semaines).
    L'arrondi se fait au nombre entier superieur.

    Args:
        mois_travailles: nombre de mois de travail effectif.
    Returns:
        dict avec jours_acquis, plafond et la regle appliquee.
    """
    bruts = config.CONGES_PAR_MOIS * float(mois_travailles)
    jours = min(math.ceil(bruts), config.CONGES_PLAFOND)
    return {
        "mois_travailles": mois_travailles,
        "jours_acquis": jours,
        "plafond": config.CONGES_PLAFOND,
        "regle": f"{config.CONGES_PAR_MOIS} j/mois ouvrable, plafond {config.CONGES_PLAFOND}",
    }


@tool
def solde_conges(nom: str) -> dict:
    """Calcule le solde de conges d'un employe (droit annuel - jours deja pris).

    Args:
        nom: nom de l'employe (recherche dans la BDD).
    Returns:
        dict avec droit_annuel, jours_pris, solde.
    """
    emp = database.find_employe(nom)
    if emp is None:
        return {"erreur": f"Employe '{nom}' introuvable."}
    droit = config.CONGES_PLAFOND
    pris = emp.get("jours_conges_pris", 0)
    return {
        "employe": emp["nom"],
        "droit_annuel": droit,
        "jours_pris": pris,
        "solde": droit - pris,
    }


@tool
def calc_prime_anciennete(annees: int) -> dict:
    """Determine le pourcentage de prime d'anciennete selon les annees revolues.

    Args:
        annees: nombre d'annees d'anciennete.
    Returns:
        dict avec le pourcentage applicable et le seuil atteint.
    """
    applicable, seuil_atteint = 0, None
    for seuil, pct in sorted(config.PRIME_ANCIENNETE_SEUILS.items()):
        if annees >= seuil:
            applicable, seuil_atteint = pct, seuil
    return {
        "annees": annees,
        "prime_pct": applicable,
        "seuil_atteint": seuil_atteint,
        "bareme": config.PRIME_ANCIENNETE_SEUILS,
    }


@tool
def conges_exceptionnels(evenement: str) -> dict:
    """Donne le nombre de jours de conges exceptionnels pour un evenement familial.

    Args:
        evenement: ex: "mariage", "naissance", "deces parent", "demenagement".
    Returns:
        dict avec le nombre de jours, ou la liste des evenements connus si non trouve.
    """
    ev = evenement.strip().lower()
    for key, jours in config.CONGES_EXCEPTIONNELS.items():
        if key in ev or ev in key:
            return {"evenement": evenement, "jours": jours}
    return {
        "evenement": evenement,
        "jours": None,
        "evenements_connus": list(config.CONGES_EXCEPTIONNELS.keys()),
    }


ALL_TOOLS = [
    search_article,
    get_employe,
    list_employes,
    calc_anciennete,
    calc_conges,
    solde_conges,
    calc_prime_anciennete,
    conges_exceptionnels,
]
