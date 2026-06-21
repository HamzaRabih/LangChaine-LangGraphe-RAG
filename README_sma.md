# 📓 SMA — Notebook d'introduction aux agents (LangChain / LangGraph)

Notebook pédagogique [`sma.ipynb`](sma.ipynb) qui présente, étape par étape, les **briques
fondamentales d'un agent LLM** avec LangChain. Il sert de base théorique au projet
[**Assistant RH**](assistant_rh/README.md).

---

## 🎯 Objectif

Apprendre à construire un agent avec `create_agent` et à lui ajouter, progressivement :
les **modèles**, un **middleware** de sélection dynamique, la **mémoire** de conversation et
des **tools**.

---

## 🗂️ Contenu du notebook

| Section | Concept illustré |
|---|---|
| **1. Agent simple** | `create_agent(model, system_prompt)` + `invoke` |
| **Initialisation des LLMs** | `ChatGoogleGenerativeAI` (Gemini) et `ChatOllama` (local) |
| **Dynamic Model** | Middleware `@wrap_model_call` : choisir le modèle selon le contexte (`env`) |
| **Mémoire** | `InMemorySaver` + `thread_id` (et exemple `PostgresSaver` commenté) |
| **Tools — basiques** | `@tool get_meteo`, `@tool get_employee_info` |
| **Tools — DuckDuckGo** | `@tool web_search` via `ddgs` (sans clé API) |
| **Tools — Tavily** | `@tool search_web` via `langchain-tavily` (clé `TAVILY_API_KEY`) |

---

## ⚙️ Pré-requis

- Python ≥ 3.13, [`uv`](https://docs.astral.sh/uv/)
- Clé API Google Gemini dans `.env` :
  ```env
  GOOGLE_API_KEY=votre_cle_api
  ```
- *(Optionnel)* [Ollama](https://ollama.com/) installé et un modèle téléchargé, pour les
  cellules utilisant `ChatOllama`.
- *(Optionnel)* `TAVILY_API_KEY` dans `.env` pour la cellule de recherche Tavily.

---

## ▶️ Lancer le notebook

```bash
# via VS Code : ouvrir sma.ipynb et sélectionner le noyau .venv
# ou via Jupyter :
uv run jupyter lab sma.ipynb
```

---

## 🔗 Liens

- ⬅️ [README racine du dépôt](README.md)
- ➡️ [Projet Assistant RH (application complète)](assistant_rh/README.md)
