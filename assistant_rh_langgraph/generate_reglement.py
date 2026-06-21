"""Genere le PDF du reglement interieur (coherent avec les regles de config.py).

Lancer depuis la racine du projet :
    uv run --with fpdf2 python assistant_rh/generate_reglement.py
"""
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUT_DIR = Path(__file__).parent / "documents"
OUT_PDF = OUT_DIR / "reglement_interieur.pdf"

# (texte, est_titre)
REGLEMENT = [
    ("Règlement intérieur - Entreprise (TP)", True),
    ("Version 1.0 - Direction des Ressources Humaines", False),
    ("", False),
    (
        "Le présent règlement intérieur fixe les règles applicables à l'ensemble "
        "des salariés en matière d'organisation du travail, de congés et de "
        "discipline. Il complète le contrat de travail.",
        False,
    ),
    ("", False),

    ("Article 1 - Horaires et temps de travail", True),
    (
        "La durée hebdomadaire de travail est de 35 heures. Les horaires de "
        "référence sont de 9h00 à 17h00 du lundi au vendredi, avec une pause "
        "déjeuner d'une heure.",
        False,
    ),
    ("", False),

    ("Article 2 - Télétravail", True),
    (
        "Le télétravail est autorisé jusqu'à 2 jours par semaine, sous réserve de "
        "l'accord du responsable hiérarchique et d'une ancienneté minimale de 6 "
        "mois. Les jours de présence obligatoire sont définis par chaque service.",
        False,
    ),
    ("", False),

    ("Article 3 - Période d'essai", True),
    (
        "La période d'essai est de 2 mois pour les employés et de 4 mois pour les "
        "cadres, renouvelable une fois. Durant cette période, le contrat peut être "
        "rompu par l'une ou l'autre des parties avec un délai de prévenance.",
        False,
    ),
    ("", False),

    ("Article 4 - Congés payés", True),
    (
        "Les salariés acquièrent 2,5 jours ouvrables de congés payés par mois de "
        "travail effectif, soit 30 jours ouvrables (5 semaines) pour une année "
        "complète. La période de référence s'étend du 1er juin au 31 mai.",
        False,
    ),
    (
        "Les demandes de congés doivent être soumises au moins 2 semaines à "
        "l'avance et validées par le responsable.",
        False,
    ),
    ("", False),

    ("Article 5 - Congés exceptionnels", True),
    (
        "Des congés exceptionnels sont accordés pour évènements familiaux : "
        "mariage ou PACS du salarié 4 jours ; naissance ou adoption 3 jours ; "
        "décès du conjoint 3 jours ; décès d'un enfant 5 jours ; décès d'un "
        "parent 3 jours ; déménagement 1 jour.",
        False,
    ),
    ("", False),

    ("Article 6 - Ancienneté et prime", True),
    (
        "L'ancienneté est calculée à compter de la date d'embauche. Une prime "
        "d'ancienneté est versée selon le barème suivant : 3% après 3 ans, 6% "
        "après 6 ans, 9% après 9 ans, 12% après 12 ans et 15% après 15 ans. Le "
        "pourcentage retenu est celui du plus haut seuil atteint.",
        False,
    ),
    ("", False),

    ("Article 7 - Absences", True),
    (
        "Toute absence doit être justifiée dans un délai de 48 heures. Les arrêts "
        "maladie doivent être transmis au service RH accompagnés du certificat "
        "médical.",
        False,
    ),
    ("", False),

    ("Article 8 - Préavis de démission", True),
    (
        "En cas de démission, le salarié respecte un préavis de 1 mois (employés) "
        "ou de 3 mois (cadres), sauf dispense accordée par l'employeur.",
        False,
    ),
    ("", False),

    ("Article 9 - Confidentialité et données", True),
    (
        "Les informations relatives à la rémunération et aux données personnelles "
        "des salariés sont strictement confidentielles et ne peuvent être "
        "communiquées qu'aux personnes habilitées (service RH, management).",
        False,
    ),
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    for text, is_title in REGLEMENT:
        if not text:
            pdf.ln(3)
            continue
        if is_title:
            pdf.set_font("Helvetica", "B", 13)
        else:
            pdf.set_font("Helvetica", size=11)
        # new_x=LMARGIN + new_y=NEXT : chaque bloc passe correctement a la ligne suivante.
        pdf.multi_cell(pdf.epw, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.output(str(OUT_PDF))
    print(f"PDF cree : {OUT_PDF}")


if __name__ == "__main__":
    main()
