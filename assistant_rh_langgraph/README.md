<div align="center">

# 🧑‍💼 Assistant RH — version **LangGraph**

**Le même assistant RH, mais l'agent est construit explicitement avec un graphe LangGraph**
(`StateGraph`, nœud agent, `ToolNode`, arêtes conditionnelles) au lieu du prebuilt `create_agent`.

`LangGraph` · `Google Gemini` · `ChromaDB` · `HuggingFace` · `Streamlit`

</div>

---

## 🎯 Pourquoi cette version ?

La version [`assistant_rh/`](../assistant_rh/README.md) utilise `create_agent` (haut niveau : la
boucle agent↔tools et le middleware sont gérés automatiquement). **Cette version reconstruit la
même logique à la main avec LangGraph**, pour montrer explicitement le graphe d'exécution.

| | `assistant_rh` (create_agent) | `assistant_rh_langgraph` (StateGraph) |
|---|---|---|
| Boucle agent ↔ tools | implicite (prebuilt) | **explicite** (`add_conditional_edges` + `ToolNode`) |
| Choix du modèle / rôle | `@wrap_model_call` (middleware) | **logique dans le nœud `agent`** |
| Mémoire | `checkpointer` | `checkpointer` (identique) |
| État | géré par le prebuilt | **`State` TypedDict + `add_messages`** |

---

## 🔀 Le graphe

<div align="center">

![Graphe LangGraph de l'Assistant RH](graph.png)

</div>

```
                 ┌───────────────────────────────┐
   START ─────►  │            agent               │
                 │  - lit le role (config)        │
                 │  - choisit le modèle Gemini    │
                 │  - injecte l'instruction rôle  │
                 │  - LLM.bind_tools().invoke()   │
                 └───────────────┬───────────────┘
                                 │ tools_condition
                 ┌───────────────┴───────────────┐
        (tool_calls ?)                       (sinon)
                 │                                │
                 ▼                                ▼
          ┌────────────┐                        END
          │   tools    │  ToolNode (exécute les tools)
          └─────┬──────┘
                │  (retour)
                └────────────►  agent
```

Code : [`graph.py`](graph.py)
```python
builder = StateGraph(State)
builder.add_node("agent", agent_node)          # nœud LLM (choix modèle selon le rôle)
builder.add_node("tools", ToolNode(ALL_TOOLS)) # exécution des tools
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)  # -> "tools" ou END
builder.add_edge("tools", "agent")
graph = builder.compile(checkpointer=InMemorySaver())
```

Le **rôle** est transmis à l'exécution via `config["configurable"]["role"]` et lu dans le nœud
`agent` (c'est là qu'on choisit `gemini-2.5-flash` pour *manager* ou `gemini-2.5-flash-lite`
pour *employé*, et qu'on injecte l'instruction de confidentialité).

---

## 🧰 Composants réutilisés (identiques à `assistant_rh`)

- **RAG** — [`rag.py`](rag.py) : règlement PDF → embeddings HuggingFace → Chroma persistant.
- **8 Tools** — [`tools.py`](tools.py) : `search_article`, `get_employe`, `list_employes`,
  `calc_anciennete`, `calc_conges`, `solde_conges`, `calc_prime_anciennete`,
  `conges_exceptionnels`.
- **BDD** — [`data/employes.json`](data/employes.json) via [`database.py`](database.py).
- **Règles RH & rôles** — [`config.py`](config.py).

---

## 📦 Structure

```
assistant_rh_langgraph/
├── app.py                  # Interface Streamlit (utilise le graphe compilé)
├── graph.py                # ⭐ StateGraph : nœuds agent/tools + arêtes + mémoire
├── models.py               # Gemini flash / flash-lite
├── tools.py                # Les 8 tools (RAG + BDD + calculs)
├── rag.py                  # Règlement → Chroma persistant
├── database.py             # Accès BDD employés
├── config.py               # Règles RH, chemins, rôles
├── generate_reglement.py   # Génère le PDF du règlement
├── inspect_vectordb.py     # Observabilité
├── data/employes.json      # Base employés
└── documents/reglement_interieur.pdf
```

---

## 🚀 Démarrage

`.env` à la racine du projet :
```env
GOOGLE_API_KEY=votre_cle_api
```

```bash
# (optionnel) régénérer le PDF du règlement
uv run --with fpdf2 python assistant_rh_langgraph/generate_reglement.py

# lancer l'application
uv run streamlit run assistant_rh_langgraph/app.py
```

---

## 🎬 Scénario de démonstration

| Étape | Question | Démontre |
|---|---|---|
| 1 | « Que dit le règlement sur le télétravail ? » | RAG (agent → tools → agent) |
| 2 | « Quelle est l'ancienneté de Hamza ? » | `get_employe` + `calc_anciennete` (2 tours dans le graphe) |
| 3 | « Combien de congés pour 8 mois ? » | `calc_conges` |
| 4 | « Et pour 11 mois ? » | Mémoire (checkpointer) |
| 5 | Passer en **manager**, demander un salaire | Choix de modèle + confidentialité dans le nœud |

---

## 🔬 Observabilité

```bash
uv run python assistant_rh_langgraph/inspect_vectordb.py --samples 3 --dims 8
```

---

🔗 Voir aussi : [README racine](../README.md) · [version create_agent](../assistant_rh/README.md)
