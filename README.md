# TP3 – AI Agents avec LangChain & LangGraph

> **Partie 1 – Agent simple avec LangChain**

Ce projet illustre la création d'agents IA avec [LangChain](https://python.langchain.com/) et [LangGraph](https://langchain-ai.github.io/langgraph/).
Cette première partie (notebook [`sma.ipynb`](sma.ipynb)) couvre, de manière progressive, les briques fondamentales d'un agent : initialisation des LLMs, invocation, sélection dynamique de modèle, mémoire conversationnelle et utilisation d'outils (*tools*).

---

## 🎯 Objectifs

- Créer un agent simple avec `create_agent`.
- Utiliser plusieurs fournisseurs de LLM : **Google Gemini** (cloud) et **Ollama** (local).
- Sélectionner dynamiquement le modèle selon le contexte d'exécution (`test` / `prod`) via un *middleware*.
- Ajouter la **mémoire** conversationnelle à un agent (`InMemorySaver`, et exemple avec PostgreSQL).
- Doter l'agent d'**outils** : fonctions personnalisées et recherche web (DuckDuckGo, Tavily).

---

## 🧱 Contenu du notebook `sma.ipynb`

| Section | Description |
|--------|-------------|
| **1. Initialisation des LLMs** | Configuration de `ChatGoogleGenerativeAI` (`gemini-2.5-flash`) et `ChatOllama` (modèle local). |
| **2. Agent simple** | Création d'un agent avec `create_agent` et envoi d'un prompt via `invoke`. |
| **3. Dynamic Model** | Middleware `wrap_model_call` qui choisit le modèle (`basic_llm` ou `advanced_llm`) selon `context["env"]`. |
| **4. Mémoire** | Comparaison agent sans mémoire vs agent avec `InMemorySaver` (suivi via `thread_id`). Exemple de persistance avec `PostgresSaver`. |
| **5. Tools** | Outils personnalisés (`get_meteo`, `get_employee_info`) appelés automatiquement par l'agent. |
| **6. Recherche web** | Intégration de **DuckDuckGo** (`ddgs`) et de **Tavily** (`langchain-tavily`) comme outils de recherche. |

---

## ⚙️ Prérequis

- **Python ≥ 3.13** (voir [`.python-version`](.python-version))
- [**uv**](https://docs.astral.sh/uv/) pour la gestion des dépendances et de l'environnement virtuel
- [**Ollama**](https://ollama.com/) installé et lancé localement (pour les modèles locaux)
- Des clés d'API valides (voir [Configuration](#-configuration))

---

## 🚀 Installation

```bash
# Cloner le dépôt puis se placer dans le dossier
cd TP3-AI-Agents-langchain-langGraph

# Installer les dépendances et créer l'environnement virtuel
uv sync
```

Lancer un modèle local avec Ollama (exemple) :

```bash
ollama pull gemma3:4b
ollama serve
```

> ℹ️ Adaptez le nom du modèle Ollama dans le notebook à celui que vous avez téléchargé.

---

## 🔑 Configuration

Créez un fichier `.env` à la racine du projet contenant vos clés d'API :

```dotenv
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

- **GOOGLE_API_KEY** : requise pour les modèles Gemini — [Google AI Studio](https://aistudio.google.com/app/apikey)
- **TAVILY_API_KEY** : requise pour l'outil de recherche Tavily — [Tavily](https://tavily.com/)
- **OPENAI_API_KEY** : optionnelle (présente pour les exemples utilisant OpenAI)

> ⚠️ Le fichier `.env` est ignoré par Git ([`.gitignore`](.gitignore)) — ne committez jamais vos clés.

---

## ▶️ Utilisation

Ouvrez le notebook dans Jupyter ou VS Code et exécutez les cellules dans l'ordre :

```bash
uv run jupyter notebook sma.ipynb
```

Le point d'entrée minimal [`main.py`](main.py) peut être lancé avec :

```bash
uv run main.py
```

---

## 📦 Principales dépendances

| Paquet | Rôle |
|--------|------|
| `langchain`, `langgraph` | Framework d'agents et orchestration |
| `langchain-google-genai` | Intégration des modèles Google Gemini |
| `langchain-ollama` | Intégration des modèles locaux Ollama |
| `langchain-openai` | Intégration des modèles OpenAI |
| `langchain-tavily`, `ddgs` | Outils de recherche web (Tavily, DuckDuckGo) |
| `python-dotenv` | Chargement des variables d'environnement |
| `ipykernel`, `ipython` | Exécution du notebook |

La liste complète figure dans [`pyproject.toml`](pyproject.toml).

---

## 📁 Structure du projet

```
TP3-AI-Agents-langchain-langGraph/
├── sma.ipynb          # Notebook principal – Partie 1 (agent simple)
├── main.py            # Point d'entrée minimal
├── pyproject.toml     # Dépendances et configuration du projet
├── uv.lock            # Verrouillage des versions (uv)
├── .python-version    # Version de Python (3.13)
├── .env               # Clés d'API (non versionné)
└── README.md
```

---

## 👤 Auteur

**Hamza RABIH** — TP3, Agentic AI (II-BDCC, S3)
