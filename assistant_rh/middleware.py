"""Middleware de personnalisation selon le ROLE (employe / manager).

Selon context["role"], il :
- choisit le modele (manager -> gemini-2.5-flash ; employe -> gemini-2.5-flash-lite) ;
- injecte une instruction de role dans la requete (ton + confidentialite).

Montre qu'un middleware peut a la fois changer le modele ET modeler le prompt.
"""
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain.messages import SystemMessage

from . import config
from .models import ADVANCED_MODEL, BASIC_MODEL, advanced_llm, basic_llm


@wrap_model_call
def role_based_personalization(request: ModelRequest, handler) -> ModelResponse:
    role = "employe"
    try:
        role = request.runtime.context.get("role", "employe")
    except AttributeError:
        pass

    if role == "manager":
        model, model_name = advanced_llm, ADVANCED_MODEL
    else:
        model, model_name = basic_llm, BASIC_MODEL
    print(f"[middleware] role={role} -> {model_name}")

    instruction = config.ROLE_INSTRUCTIONS.get(role, "")
    new_messages = [SystemMessage(content=instruction)] + list(request.messages)

    return handler(request.override(model=model, messages=new_messages))
