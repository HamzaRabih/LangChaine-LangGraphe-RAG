"""Assistant RH (version LangGraph) : RAG + tools + memoire + selection de modele par role.

Meme fonctionnalite que le projet assistant_rh, mais l'agent est construit explicitement
avec un StateGraph LangGraph (noeud agent + ToolNode + aretes conditionnelles) au lieu du
prebuilt create_agent.
"""
