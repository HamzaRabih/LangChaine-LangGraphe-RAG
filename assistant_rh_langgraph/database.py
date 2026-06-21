"""Acces a la base de donnees employes (BDD simulee, fichier JSON).

Dans un vrai projet ce module ferait des requetes SQL ; ici on lit un JSON, ce qui
suffit pour le TP et garde l'interface (get_all / find).
"""
import json
from functools import lru_cache

from . import config


@lru_cache(maxsize=1)
def get_all() -> list[dict]:
    """Charge tous les employes (cache en memoire)."""
    if not config.BDD_PATH.exists():
        return []
    return json.loads(config.BDD_PATH.read_text(encoding="utf-8"))


def find_employe(nom: str) -> dict | None:
    """Recherche tolerante par nom (sous-chaine, insensible a la casse)."""
    nom_norm = (nom or "").strip().lower()
    if not nom_norm:
        return None
    employes = get_all()
    # 1) correspondance exacte, 2) sous-chaine, 3) par prenom/mot
    for emp in employes:
        if emp["nom"].lower() == nom_norm:
            return emp
    for emp in employes:
        if nom_norm in emp["nom"].lower():
            return emp
    for emp in employes:
        if any(part in emp["nom"].lower().split() for part in nom_norm.split()):
            return emp
    return None
