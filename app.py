import streamlit as st
from agents.orchestrator import answer_query, get_agent_map

st.set_page_config(page_title="Agentic FM Solver", page_icon="💰", layout="wide")

st.title("💰 Agentic Financial Mathematics Solver")
st.caption("One chat window powered by an Orchestrator Agent and specialized FM subagents.")

with st.sidebar:
    st.header("Agent System")
    st.code("""
User
 ↓
Orchestrator Agent
 ├── TVM Agent
 ├── Annuity Agent
 ├── Loan Agent
 ├── Refinance Agent
 └── Bond Agent
""", language="text")

    st.header("Current Status")
    st.success("TVM Agent: Active")
    st.info("Annuity, Loan, Refinance, and Bond Agents: Planned")

    st.header("Answer Protocol")
    st.write("- Given")
    st.write("- Formula")
    st.write("- Substitution")
    st.write("- Final Answer")

    st.header("Sign Convention")
    st.write("Cash inflows are positive.")
    st.write("Cash outflows are negative.")
    st.write("Equation of value uses a stated focal date.")

with st.expander("View agent responsibilities"):
    for agent, details in get_agent_map().items():
        st.subheader(agent)
        st.write(details)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ask me a TVM question. Example: Find the present value of ₹10,000 due in 3 years at 8% effective annual interest."
        }
    ]

if "logs" not in st.session_state:
    st.session_state.logs = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask a Financial Mathematics question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    result = answer_query(prompt)
    response = result["answer"]

    st.session_state.logs.append(result["log"])
    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)

with st.expander("System Protocol / Routing Log"):
    if st.session_state.logs:
        for i, log in enumerate(st.session_state.logs, start=1):
            st.markdown(f"**Turn {i}**")
            st.json(log)
    else:
        st.write("No routing logs yet.")
