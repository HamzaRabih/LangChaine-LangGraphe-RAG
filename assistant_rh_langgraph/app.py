"""Application Streamlit : Assistant RH (version LangGraph explicite).

Lancer depuis la racine du projet :
    streamlit run assistant_rh_langgraph/app.py
"""
import sys
from pathlib import Path
from uuid import uuid4

# Permet d'importer le package quand streamlit execute ce fichier comme script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from langchain_core.messages import HumanMessage

from assistant_rh_langgraph import rag, tools
from assistant_rh_langgraph.graph import build_graph
from assistant_rh_langgraph.models import ADVANCED_MODEL, BASIC_MODEL


def model_for_role(role: str) -> str:
    return ADVANCED_MODEL if role == "manager" else BASIC_MODEL


def render_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(p for p in parts if p)
    return str(content)


def extract_tool_calls(messages) -> list[str]:
    calls = []
    for msg in messages:
        for call in getattr(msg, "tool_calls", None) or []:
            calls.append(f"{call['name']}({call.get('args', {})})")
    return calls


def init_state():
    if "graph" not in st.session_state:
        st.session_state.graph = build_graph()
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid4())
    st.session_state.setdefault("retriever", None)
    st.session_state.setdefault("reglement_source", None)
    st.session_state.setdefault("history", [])

    if not st.session_state.get("reglement_ready"):
        retriever, source = rag.ensure_reglement_retriever()
        st.session_state.retriever = retriever
        st.session_state.reglement_source = source
        st.session_state.reglement_ready = retriever is not None
    tools.set_reglement_retriever(st.session_state.retriever)


def main():
    st.set_page_config(page_title="Assistant RH (LangGraph)", layout="wide")
    init_state()

    st.subheader("Assistant RH - LangGraph", divider="blue")
    st.caption("StateGraph explicite (agent + ToolNode) + RAG + BDD employes + memoire "
               "+ selection de modele par role.")

    with st.sidebar:
        st.title("Configuration")

        # --- Reglement (RAG, persistant) ---
        st.subheader("Reglement interieur")
        src = st.session_state.reglement_source
        if st.session_state.retriever is not None:
            label = {"persisted": "persiste", "default": "indexe depuis documents/"}.get(src, src)
            st.success(f"Reglement charge ({label}).")
        else:
            st.error("Aucun reglement. Depose un PDF dans assistant_rh_langgraph/documents/ "
                     "ou charge-le ci-dessous.")
        reglement_pdf = st.file_uploader("Mettre a jour le reglement (PDF)",
                                         accept_multiple_files=True, key="reg_up")
        if st.button("Mettre a jour le reglement") and reglement_pdf:
            with st.spinner("Indexation..."):
                retriever, err = rag.index_reglement(reglement_pdf)
            if err:
                st.warning(err)
            else:
                st.session_state.retriever = retriever
                st.session_state.reglement_source = "persisted"
                st.session_state.reglement_ready = True
                tools.set_reglement_retriever(retriever)
                st.success("Reglement mis a jour et persiste.")

        st.divider()

        # --- Role (selection de modele dans le noeud du graphe) ---
        st.subheader("Role")
        role = st.radio(
            "Vous etes :", options=["employe", "manager"], horizontal=True,
            help="employe = ton vulgarise, infos limitees (gemini-2.5-flash-lite) ; "
                 "manager = reponses completes, acces a tous les dossiers (gemini-2.5-flash)",
        )
        st.session_state.role = role
        st.caption(f"Modele actif : **{model_for_role(role)}**")

        st.divider()
        if st.button("Nouvelle conversation"):
            st.session_state.thread_id = str(uuid4())
            st.session_state.history = []
            st.success("Memoire reinitialisee (nouveau thread).")

    role = st.session_state.get("role", "employe")
    st.info(f"Role : **{role}**  -  modele actif : **{model_for_role(role)}** "
            "(modifiable dans la sidebar)")

    for r, content in st.session_state.history:
        with st.chat_message(r):
            st.markdown(content)

    question = st.chat_input("Posez votre question RH...")
    if not question:
        return

    if st.session_state.retriever is None:
        st.warning("Charge d'abord le reglement interieur (PDF) dans la sidebar.")
        return

    st.session_state.history.append(("user", question))
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner(f"Reflexion ({role})..."):
            result = st.session_state.graph.invoke(
                {"messages": [HumanMessage(content=question)]},
                config={"configurable": {"thread_id": st.session_state.thread_id, "role": role}},
            )
        answer = render_content(result["messages"][-1].content)
        st.markdown(answer)

        tool_calls = extract_tool_calls(result["messages"])
        if tool_calls:
            with st.expander(f"Tools appeles ({len(tool_calls)})"):
                for tc in tool_calls:
                    st.code(tc)

    st.session_state.history.append(("assistant", answer))


if __name__ == "__main__":
    main()
