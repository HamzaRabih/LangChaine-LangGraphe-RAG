"""Construction de l'agent RH : create_agent + tools + middleware + memoire."""
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from .middleware import role_based_personalization
from .models import basic_llm
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

memory = InMemorySaver()


def build_agent():
    """Cree l'agent. Le modele par defaut est remplace au runtime par le middleware."""
    return create_agent(
        model=basic_llm,
        system_prompt=SYSTEM_PROMPT,
        tools=ALL_TOOLS,
        middleware=[role_based_personalization],
        checkpointer=memory,
    )
