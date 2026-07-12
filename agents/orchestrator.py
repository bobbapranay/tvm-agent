from agents.tvm_agent import solve_tvm_query

def get_agent_map() -> dict:
    """
    Return the planned multi-agent architecture and each agent's responsibility.

    Returns:
        dict: Agent names mapped to short responsibility descriptions.
    """
    return {
        "Orchestrator Agent": "Receives the user's question, identifies the FM topic, and routes the request to the correct specialized agent.",
        "TVM Agent": "Handles PV, FV, interest rates, periods, rate conversions, force of interest, and equation of value problems.",
        "Annuity Agent": "Will solve annuity-immediate, annuity-due, perpetuity, deferred annuity, PV, AV, and payment problems.",
        "Loan Agent": "Will handle loan payments, outstanding balances, amortization schedules, principal repayment, and interest breakdowns.",
        "Refinance Agent": "Will compare existing loans with new loan options to calculate savings, payment changes, and break-even periods.",
        "Bond Agent": "Will handle bond pricing, yield, redemption value, coupon cashflows, duration, and interest-rate sensitivity."
    }

TVM_KEYWORDS = [
    "present value", "pv", "future value", "fv", "interest", "rate",
    "effective", "nominal", "force", "delta", "equation of value",
    "cashflow", "cashflows", "cash flow", "discount", "accumulate",
    "accumulated", "time value", "tvm", "period", "years", "months",
    "grow", "become", "compounded"
]

ANNUITY_KEYWORDS = ["annuity", "annuity due", "annuity-immediate", "perpetuity"]
LOAN_KEYWORDS = ["loan payment", "emi", "amortization", "outstanding balance"]
REFINANCE_KEYWORDS = ["refinance", "refinancing", "break-even", "savings"]
BOND_KEYWORDS = ["bond", "coupon", "yield", "duration", "redemption"]

def classify_agent(user_query: str) -> str:
    """
    Classify the user's question and select the most appropriate FM subagent.

    Parameters:
        user_query (str): Natural language user question.

    Returns:
        str: Selected agent name.
    """
    query = user_query.lower()

    if any(word in query for word in REFINANCE_KEYWORDS):
        return "Refinance Agent"
    if any(word in query for word in BOND_KEYWORDS):
        return "Bond Agent"
    if any(word in query for word in LOAN_KEYWORDS):
        return "Loan Agent"
    if any(word in query for word in ANNUITY_KEYWORDS):
        return "Annuity Agent"
    if any(word in query for word in TVM_KEYWORDS):
        return "TVM Agent"

    return "Unknown"

def answer_query(user_query: str) -> dict:
    """
    Route the user query to the correct subagent and return the answer with a routing log.

    Parameters:
        user_query (str): Natural language FM question.

    Returns:
        dict: Contains answer text and protocol log.
    """
    selected_agent = classify_agent(user_query)

    log = {
        "user_query": user_query,
        "selected_agent": selected_agent,
        "active_agent_status": "active" if selected_agent == "TVM Agent" else "planned",
        "routing_reason": "",
        "tool_used": None,
        "protocol": "Given → Formula → Substitution → Final Answer"
    }

    if selected_agent == "TVM Agent":
        answer, tool_used = solve_tvm_query(user_query)
        log["routing_reason"] = "The query matches TVM concepts such as PV, FV, rates, periods, or equation of value."
        log["tool_used"] = tool_used
        return {
            "answer": f"**Selected Agent:** TVM Agent  \n**Tool Used:** `{tool_used}`\n\n{answer}",
            "log": log
        }

    if selected_agent == "Unknown":
        log["routing_reason"] = "No supported FM topic was confidently detected."
        return {
            "answer": "**Selected Agent:** None\n\nI can currently solve TVM questions only. Future versions will support annuities, loans, refinancing, and bonds.",
            "log": log
        }

    log["routing_reason"] = f"The query matches {selected_agent}, but that subagent is not active yet."
    return {
        "answer": f"**Selected Agent:** {selected_agent}\n\n{selected_agent} is part of the planned multi-agent architecture, but only the TVM Agent is active in this version.",
        "log": log
    }
