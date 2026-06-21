<div align="center">

# 🤖 TP3 — Agentic AI · LangChain / LangGraph

Dépôt regroupant **deux volets** complémentaires : un **notebook d'apprentissage** des
patterns agentiques et une **application complète** qui les met en œuvre.

`LangChain` · `LangGraph` · `Google Gemini` · `ChromaDB` · `HuggingFace` · `Streamlit`

</div>

---

## 📚 Les deux projets

### 1. 📓 SMA — Notebook d'introduction aux agents
Notebook pédagogique [`sma.ipynb`](sma.ipynb) présentant pas à pas les briques d'un agent LLM :
`create_agent`, choix des modèles (Gemini / Ollama), **middleware** de sélection dynamique,
**mémoire** conversationnelle et **tools** (météo, employé, recherche web DuckDuckGo / Tavily).

📖 **Documentation : [README_sma.md](README_sma.md)**

### 2. 🧑‍💼 Assistant RH — Application complète *(create_agent)*
Chatbot agentique pour les Ressources Humaines, qui combine les 4 piliers d'un agent moderne :
- 🔍 **RAG** sur le règlement intérieur (PDF) ;
- 🛠️ **Tools** : base de données employés + calculs RH déterministes (congés, ancienneté, primes) ;
- ⚙️ **Middleware** : adaptation au rôle (employé / manager) ;
- 🧠 **Mémoire** de conversation.

Implémentation avec le prebuilt **`create_agent`** de LangChain (haut niveau).

📖 **Documentation : [assistant_rh/README.md](assistant_rh/README.md)**

### 3. 🔀 Assistant RH — version **LangGraph**
La **même application**, mais l'agent est reconstruit explicitement avec un **graphe LangGraph**
(`StateGraph`, nœud agent, `ToolNode`, arêtes conditionnelles) au lieu de `create_agent` — pour
montrer en détail la boucle d'exécution agent ⇄ tools.

📖 **Documentation : [assistant_rh_langgraph/README.md](assistant_rh_langgraph/README.md)**

---

## 🗺️ Structure du dépôt

```
TP3-AI-Agents-langchain-langGraph/
├── sma.ipynb                  # Projet 1 : notebook d'apprentissage   → README_sma.md
├── README_sma.md              # Documentation du notebook
├── assistant_rh/              # Projet 2 : Assistant RH (create_agent) → assistant_rh/README.md
│   └── README.md
├── assistant_rh_langgraph/    # Projet 3 : Assistant RH (LangGraph)    → assistant_rh_langgraph/README.md
│   └── README.md
├── pyproject.toml             # Dépendances (gérées par uv)
├── .env                       # Clés API (non versionné)
└── README.md                  # Ce fichier
```

---

## ⚙️ Pré-requis communs

- **Python ≥ 3.13** et [`uv`](https://docs.astral.sh/uv/)
- Un fichier `.env` à la racine :
  ```env
  GOOGLE_API_KEY=votre_cle_api
  # Optionnelles (notebook) : TAVILY_API_KEY, et Ollama pour les modèles locaux
  ```
  *(Clé Gemini : [Google AI Studio](https://aistudio.google.com/app/apikey).)*

Installation des dépendances :
```bash
uv sync
```

---

## 🚀 Démarrage rapide

| Projet | Commande |
|---|---|
| 📓 Notebook SMA | `uv run jupyter lab sma.ipynb` *(ou l'ouvrir dans VS Code)* |
| 🧑‍💼 Assistant RH *(create_agent)* | `uv run streamlit run assistant_rh/app.py` |
| 🔀 Assistant RH *(LangGraph)* | `uv run streamlit run assistant_rh_langgraph/app.py` |

---

## 👤 Auteur

**Hamza RABIH** — TP3, Agentic AI (II-BDCC, S3)
