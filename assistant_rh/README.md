<div align="center">

# 🧑‍💼 Assistant RH — Agent Conversationnel Intelligent

**Chatbot agentique pour les Ressources Humaines : RAG · Tools · Middleware · Mémoire**

`LangChain` · `LangGraph` · `Google Gemini` · `ChromaDB` · `HuggingFace` · `Streamlit`

</div>

---

## 📖 Présentation

**Assistant RH** est un agent conversationnel qui répond aux questions des salariés et
managers sur le **règlement intérieur** de l'entreprise et automatise les **calculs RH**
(congés, ancienneté, primes) en s'appuyant sur une **base de données employés**.

Le projet illustre, sur un cas métier concret, les **quatre piliers d'un agent LLM moderne** :

| Pilier | Mise en œuvre |
|---|---|
| 🔍 **RAG** | Le règlement intérieur (PDF) est vectorisé et interrogé via un *tool* dédié |
| 🛠️ **Tools** | 8 outils : accès base employés + calculs RH **déterministes** |
| ⚙️ **Middleware** | Adaptation dynamique au **rôle** (employé / manager) : modèle, ton, confidentialité |
| 🧠 **Mémoire** | Conversation multi-tours par `thread_id` |

> **Principe de conception clé** : les calculs (dates, montants) ne sont **jamais** confiés au
> LLM — l'agent *lit* la règle via le RAG puis *délègue* le calcul à un tool Python testable.
> On obtient ainsi des réponses **fiables et auditables**.

---

## 🏗️ Architecture

```
┌──────────────────────────── Streamlit (app.py) ────────────────────────────┐
│  Sidebar : règlement (PDF) · rôle (employé/manager) · nouvelle conversation │
│  Chat    : question utilisateur ─────────────────────────────────────────┐  │
└──────────────────────────────────────────────────────────────────────────┼──┘
                                                                            │
                          ┌─────────────────────────────────────────────────▼─┐
                          │              Agent (create_agent)                  │
                          │  system_prompt + mémoire (InMemorySaver)           │
                          └───┬───────────────────────┬───────────────────────┘
                              │                        │
              ┌───────────────▼──────────┐   ┌─────────▼───────────────────────┐
              │  Middleware (rôle)        │   │  Tools                          │
              │  @wrap_model_call         │   │  • search_article  → RAG        │
              │  employé  → flash-lite    │   │  • get_employe     → BDD JSON   │
              │  manager  → flash         │   │  • calc_*          → Python     │
              │  + instruction injectée   │   │                                 │
              └───────────────────────────┘   └───┬─────────────────┬───────────┘
                                                   │                 │
                                   ┌───────────────▼───┐   ┌─────────▼─────────┐
                                   │ ChromaDB (persist)│   │ data/employes.json│
                                   │ règlement vectorisé│   │  (base employés)  │
                                   └────────────────────┘   └───────────────────┘
```

---

## 🧰 Stack technique

| Couche | Technologie |
|---|---|
| Framework agent | **LangChain** (`create_agent`) + **LangGraph** (checkpointer) |
| LLM | **Google Gemini** `2.5-flash` (manager) / `2.5-flash-lite` (employé) |
| Embeddings | **HuggingFace** `sentence-transformers/all-MiniLM-L6-v2` (local, open source, dim 384) |
| Base vectorielle | **ChromaDB** (persistante sur disque) |
| Extraction PDF | **PyPDF2** + `RecursiveCharacterTextSplitter` |
| Interface | **Streamlit** |
| Gestion d'env. | **uv** |

---

## 📦 Structure du projet

```
assistant_rh/
├── app.py                  # Interface Streamlit
├── agent.py                # create_agent + system prompt + mémoire
├── middleware.py           # @wrap_model_call (rôle employé / manager)
├── models.py               # Modèles Gemini (flash / flash-lite)
├── tools.py                # Les 8 tools (RAG + BDD + calculs)
├── rag.py                  # Indexation/chargement du règlement (Chroma persistant)
├── database.py             # Accès à la base employés
├── config.py               # Règles RH, chemins, rôles
├── generate_reglement.py   # Génère le PDF du règlement intérieur
├── inspect_vectordb.py     # Outil d'observabilité de la base vectorielle
├── data/
│   └── employes.json       # Base de données employés (simulée)
├── documents/
│   └── reglement_interieur.pdf
└── README.md
```

---

## 🚀 Installation & démarrage

### Pré-requis
- Python ≥ 3.13, [`uv`](https://docs.astral.sh/uv/)
- Une clé API Google Gemini ([Google AI Studio](https://aistudio.google.com/app/apikey))

### Configuration
Créer un fichier `.env` à la racine du projet :
```env
GOOGLE_API_KEY=votre_cle_api
```

### Lancement
```bash
# 1) (optionnel) (re)générer le PDF du règlement intérieur
uv run --with fpdf2 python assistant_rh/generate_reglement.py

# 2) lancer l'application
uv run streamlit run assistant_rh/app.py
```
➡️ L'application est disponible sur **http://localhost:8501**.

Au démarrage, le règlement est **chargé automatiquement** : depuis le store persistant s'il
existe, sinon par indexation du PDF présent dans `documents/`.

---

## 💬 Utilisation

1. **Règlement** — chargé automatiquement ; bouton *« Mettre à jour le règlement »* pour fournir
   un autre PDF (ré-indexé et persisté).
2. **Rôle** *(middleware)* — sélectionner **employé** ou **manager** dans la barre latérale.
3. **Chat** — poser une question ; les *tools* appelés sont affichés dans un volet repliable.

---

## 🛠️ Référence des Tools

| Tool | Signature | Catégorie | Description |
|---|---|---|---|
| `search_article` | `(query)` | RAG | Recherche une règle dans le règlement intérieur |
| `get_employe` | `(nom)` | BDD | Fiche d'un employé (embauche, congés, salaire…) |
| `list_employes` | `()` | BDD | Liste des employés |
| `calc_anciennete` | `(date_embauche, date_reference="aujourd'hui")` | Calcul | Ancienneté (années / mois) |
| `calc_conges` | `(mois_travailles)` | Calcul | Congés acquis (2,5 j/mois, plafond 30) |
| `solde_conges` | `(nom)` | BDD + calcul | Droit annuel − congés déjà pris |
| `calc_prime_anciennete` | `(annees)` | Calcul | % de prime selon le barème |
| `conges_exceptionnels` | `(evenement)` | Calcul | Jours pour mariage, naissance, décès… |

---

## ⚙️ Middleware : personnalisation par rôle

Le middleware lit `context["role"]` et, pour chaque appel modèle :

| Rôle | Modèle | Comportement |
|---|---|---|
| **employé** | `gemini-2.5-flash-lite` | Ton pédagogique ; **ne divulgue pas** les données sensibles d'autrui (salaires) |
| **manager** | `gemini-2.5-flash` | Réponses complètes, cite les articles, accès à tous les dossiers |

Il **sélectionne le modèle** *et* **injecte une instruction de rôle** dans la requête —
démontrant qu'un middleware peut modeler le prompt, pas seulement changer de modèle.

---

## 🗄️ Base de données employés

Base simulée dans [`data/employes.json`](data/employes.json) (5 employés). Chaque fiche contient :
`matricule`, `nom`, `departement`, `poste`, `date_embauche`, `jours_conges_pris`,
`salaire_base`, `statut`. Le module [`database.py`](database.py) expose `get_all()` et
`find_employe(nom)` (recherche tolérante).

---

## 🔬 Observabilité

Inspecter le contenu de la base vectorielle (documents indexés + aperçu des embeddings) :
```bash
uv run python assistant_rh/inspect_vectordb.py --samples 3 --dims 8
```

---

## ✅ Tests

Les 8 tools sont validés en unitaire ; 7/8 le sont aussi de bout en bout via l'agent
(le dernier dépend uniquement du quota gratuit Gemini). Scénarios couverts :

| Composant | Exemple vérifié | Résultat |
|---|---|---|
| RAG | « Que dit le règlement sur le télétravail ? » | 2 j/sem, ancienneté 6 mois |
| BDD + calcul | « Ancienneté de Hamza ? » | 5 ans 3 mois |
| Calcul | « Congés pour 8 mois ? » | 20 jours |
| Mémoire | « Et pour 11 mois ? » | 28 jours (contexte retenu) |
| BDD | « Solde de congés de Sara ? » | 12 jours |
| Middleware | « Salaire de Fatima ? » | employé → refus / manager → 45 000 |

---

## 🎬 Scénario de démonstration

1. **RAG** — « Que dit le règlement sur le télétravail ? »
2. **BDD + calcul** — « Quelle est l'ancienneté de Hamza ? »
3. **Calcul** — « Combien de congés pour 8 mois travaillés ? »
4. **Mémoire** — « Et pour 11 mois ? »
5. **BDD** — « Quel est le solde de congés de Sara ? »
6. **Middleware** — passer en *manager* puis demander une information salariale.

---

## 🔧 Personnalisation

- **Règles RH** : ajuster les plafonds, barèmes et congés exceptionnels dans
  [`config.py`](config.py) *(garder la cohérence avec le PDF du règlement)*.
- **Employés** : éditer [`data/employes.json`](data/employes.json).
- **Règlement** : modifier [`generate_reglement.py`](generate_reglement.py) ou fournir son
  propre PDF via l'interface.

## 🗺️ Pistes d'évolution
- Mémoire persistante (`SqliteSaver` / `PostgresSaver`).
- Tools supplémentaires : `generer_bulletin_paie`, `poser_conge`, `jours_feries`.
- Suite de tests `pytest` automatisée sur les tools.

---

<div align="center">

*Projet réalisé dans le cadre du TP « Agentic AI » — LangChain / LangGraph.*

</div>
