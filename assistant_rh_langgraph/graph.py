"""Assistant RH construit explicitement avec LangGraph (StateGraph).

Contrairement a la version `create_agent` (haut niveau), on assemble ici le graphe a la
main :

    START -> agent -> (tools_condition) -> tools -> agent -> ... -> END

- `agent`  : noeud LLM. Il choisit le modele selon le ROLE (logique de "middleware"
             desormais explicite dans le noeud) et injecte l'instruction de role.
- `tools`  : ToolNode prebuilt qui execute les tools demandes par le LLM.
- arete conditionnelle `tools_condition` : si le dernier message contient des tool_calls
  -> noeud `tools`, sinon -> END.
- memoire  : checkpointer InMemorySaver (suivi par thread_id).
"""
from typing import Annotated

from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from .config import ROLE_INSTRUCTIONS
from .models import ADVANCED_MODEL, BASIC_MODEL, advanced_llm, basic_llm
from .tools import ALL_TOOLS

SYSTEM_PROMPT = """Tu es l'assistant RH de l'entreprise.
Tu reponds aux questions sur le reglement interieur et tu realises les calculs RH.

Methode :
1. Pour une question sur une REGLE (conges, teletravail, preavis, periode d'essai,
   primes...), utilise le tool search_article et cite la regle. N'appelle PAS
   search_article pour un simple calcul.
2. Pour un CALCUL (anciennete, conges, prime, solde), utilise TOUJOURS le tool dedie :
   ne calcule jamais toi-meme les dates ou les montants.
3. Si la question concerne un employe nomme, recupere d'abord sa fiche avec get_employe
   (date d'embauche, conges pris...), puis enchaine les calculs.
4. Pour l'anciennete, si aucune date de reference n'est precisee, utilise la date du
   jour par defaut (date_reference='aujourd'hui') sans la demander.
5. Reponds en francais, clairement, en Markdown.

Si une information manque, demande-la ou signale-le ; n'invente jamais de donnee.
"""

# Les deux modeles, equipes des memes tools.
_advanced_with_tools = advanced_llm.bind_tools(ALL_TOOLS)
_basic_with_tools = basic_llm.bind_tools(ALL_TOOLS)


class State(TypedDict):
    """Etat du graphe : l'historique de messages (reducer add_messages)."""
    messages: Annotated[list, add_messages]


def agent_node(state: State, config) -> dict:
    """Noeud LLM : selection du modele selon le role + injection de l'instruction."""
    role = "employe"
    try:
        role = config.get("configurable", {}).get("role", "employe")
    except Exception:
        pass

    if role == "manager":
        llm, model_name = _advanced_with_tools, ADVANCED_MODEL
    else:
        llm, model_name = _basic_with_tools, BASIC_MODEL
    print(f"[graph] role={role} -> {model_name}")

    system = SystemMessage(content=SYSTEM_PROMPT + "\n\n" + ROLE_INSTRUCTIONS.get(role, ""))
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}


def build_graph():
    """Construit et compile le graphe (avec memoire)."""
    builder = StateGraph(State)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(ALL_TOOLS))

    builder.add_edge(START, "agent")
    # tools_condition route vers "tools" si le LLM demande un tool, sinon vers END.
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    return builder.compile(checkpointer=InMemorySaver())
