import re
from tools.tvm_tools import (
    present_value,
    future_value,
    solve_rate,
    solve_n,
    nominal_to_effective,
    effective_to_nominal,
    force_to_effective,
    effective_to_force,
    equation_of_value,
)

def _numbers(text: str) -> list:
    """
    Extract numeric values from a user question.
    """
    cleaned = text.replace(",", "")
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", cleaned)]

def _rate_from_percent(value: float) -> float:
    """
    Convert a percentage-like input into decimal form.
    """
    return value / 100 if value > 1 else value

def _money(x: float) -> str:
    """
    Format a numeric value as Indian rupee currency.
    """
    return f"₹{x:,.2f}"

def _compounding_frequency(text: str):
    """
    Infer compounding frequency from natural language.
    """
    q = text.lower()
    if "monthly" in q:
        return 12
    if "quarterly" in q:
        return 4
    if "semiannual" in q or "semi-annually" in q or "semi annually" in q or "half-yearly" in q:
        return 2
    if "annually" in q or "annual" in q or "yearly" in q:
        return 1
    if "daily" in q:
        return 365
    return None

def _extract_cashflows(text: str) -> list:
    """
    Extract cashflow pairs from phrases like '-1000 at time 0'.
    """
    pattern = r"(-?\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:at|@)\s*(?:time|t)\s*(-?\d+(?:\.\d+)?)"
    pairs = re.findall(pattern, text.lower())
    return [{"amount": float(a.replace(",", "")), "time": float(t)} for a, t in pairs]

def _extract_focal_date(text: str):
    """
    Extract focal date from phrases like 'value at time 2'.
    """
    match = re.search(r"(?:value|equivalent value)\s*(?:at|@)\s*(?:time|t)\s*(-?\d+(?:\.\d+)?)", text.lower())
    return float(match.group(1)) if match else None

def _extract_interest_rate(text: str):
    """
    Extract the final percentage value as the interest rate.
    """
    matches = re.findall(r"(-?\d+(?:\.\d+)?)\s*%", text)
    return _rate_from_percent(float(matches[-1])) if matches else None


def _extract_amount_years_rate(text: str):
    """
    Extract amount, years, and percentage rate from common TVM wording.

    Handles forms like:
        - after 5 years of ₹20,000 invested at 7%
        - ₹20,000 invested for 5 years at 7%
        - 20000 for 5 years at 7%

    Returns:
        tuple | None: (amount, years, decimal_rate)
    """
    q = text.replace(",", "")

    patterns = [
        r"after\s+(\d+(?:\.\d+)?)\s+years?\s+of\s+₹?\s*(\d+(?:\.\d+)?)\s+.*?at\s+(\d+(?:\.\d+)?)\s*%",
        r"₹?\s*(\d+(?:\.\d+)?)\s+.*?(?:for|after)\s+(\d+(?:\.\d+)?)\s+years?\s+.*?at\s+(\d+(?:\.\d+)?)\s*%",
    ]

    for index, pattern in enumerate(patterns):
        match = re.search(pattern, q.lower())
        if match:
            if index == 0:
                years = float(match.group(1))
                amount = float(match.group(2))
                rate = _rate_from_percent(float(match.group(3)))
            else:
                amount = float(match.group(1))
                years = float(match.group(2))
                rate = _rate_from_percent(float(match.group(3)))
            return amount, years, rate

    return None


def solve_tvm_query(query: str) -> tuple[str, str]:
    """
    Solve a TVM query using deterministic backend tools.

    Supported concepts:
        - Present value
        - Future value / accumulated value
        - Effective interest rate
        - Number of periods
        - Nominal to effective conversion
        - Effective to nominal conversion
        - Force of interest
        - Equation of value
    """
    q = query.lower()
    nums = _numbers(query)

    try:
        if "nominal" in q and "effective" in q and len(nums) >= 1:
            rate = _rate_from_percent(nums[0])
            m = int(nums[1]) if len(nums) >= 2 else _compounding_frequency(q)
            if m is None:
                return (
                    "I need the compounding frequency, such as monthly, quarterly, semi-annually, annually, or 12 times per year.",
                    "clarification_required"
                )
            eff = nominal_to_effective(rate, m)
            return (
                "**Given:**\n"
                f"- Nominal rate = {rate:.6f}\n"
                f"- Compounding frequency = {m}\n\n"
                "**Formula:**\n"
                "Effective rate = (1 + j/m)^m - 1\n\n"
                "**Substitution:**\n"
                f"(1 + {rate:.6f}/{m})^{m} - 1\n\n"
                "**Final Answer:**\n"
                f"Effective annual rate = **{eff * 100:.4f}%**",
                "nominal_to_effective"
            )

        if ("equation of value" in q or "cashflow" in q or "cash flow" in q or "cashflows" in q) and len(nums) >= 3:
            cashflows = _extract_cashflows(query)
            rate = _extract_interest_rate(query)
            focal_date = _extract_focal_date(query)
            if not cashflows or rate is None or focal_date is None:
                return (
                    "I need cashflows in this format: `-1000 at time 0, 600 at time 1`, plus an interest rate and focal date.",
                    "clarification_required"
                )
            total = equation_of_value(cashflows, rate, focal_date)
            cf_text = ", ".join([f"{c['amount']} at t={c['time']}" for c in cashflows])
            return (
                "**Given:**\n"
                f"- Cashflows = {cf_text}\n"
                f"- Interest rate = {rate:.6f}\n"
                f"- Focal date = {focal_date}\n\n"
                "**Formula:**\n"
                "Value at focal date = Σ C(1+i)^(focal_date - t)\n\n"
                "**Substitution:**\n"
                f"Each cashflow is moved to t = {focal_date}\n\n"
                "**Final Answer:**\n"
                f"Value at focal date = **{_money(total)}**",
                "equation_of_value"
            )

        if "force" in q and "effective" in q and len(nums) >= 1:
            delta = _rate_from_percent(nums[0])
            eff = force_to_effective(delta)
            return (
                "**Given:**\n"
                f"- Force of interest δ = {delta:.6f}\n\n"
                "**Formula:**\n"
                "i = e^δ - 1\n\n"
                "**Substitution:**\n"
                f"e^{delta:.6f} - 1\n\n"
                "**Final Answer:**\n"
                f"Effective rate = **{eff * 100:.4f}%**",
                "force_to_effective"
            )

        if "force" in q and len(nums) >= 1:
            eff = _rate_from_percent(nums[0])
            delta = effective_to_force(eff)
            return (
                "**Given:**\n"
                f"- Effective rate i = {eff:.6f}\n\n"
                "**Formula:**\n"
                "δ = ln(1 + i)\n\n"
                "**Substitution:**\n"
                f"ln(1 + {eff:.6f})\n\n"
                "**Final Answer:**\n"
                f"Force of interest = **{delta:.6f}**",
                "effective_to_force"
            )

        if ("present value" in q or "pv" in q) and len(nums) >= 3:
            fv, n, rate = nums[0], nums[1], _rate_from_percent(nums[2])
            pv = present_value(fv, rate, n)
            return (
                "**Given:**\n"
                f"- FV = {_money(fv)}\n"
                f"- i = {rate:.6f}\n"
                f"- n = {n}\n\n"
                "**Formula:**\n"
                "PV = FV / (1 + i)^n\n\n"
                "**Substitution:**\n"
                f"PV = {fv} / (1 + {rate:.6f})^{n}\n\n"
                "**Final Answer:**\n"
                f"PV = **{_money(pv)}**",
                "present_value"
            )

        if ("future value" in q or "fv" in q or "accumulated value" in q or "accumulate" in q) and len(nums) >= 3:
            parsed = _extract_amount_years_rate(query)
            if parsed:
                pv, n, rate = parsed
            else:
                pv, n, rate = nums[0], nums[1], _rate_from_percent(nums[2])

            fv = future_value(pv, rate, n)
            return (
                "**Given:**\n"
                f"- PV = {_money(pv)}\n"
                f"- i = {rate:.6f}\n"
                f"- n = {n}\n\n"
                "**Formula:**\n"
                "FV = PV(1 + i)^n\n\n"
                "**Substitution:**\n"
                f"FV = {pv}(1 + {rate:.6f})^{n}\n\n"
                "**Final Answer:**\n"
                f"FV = **{_money(fv)}**",
                "future_value"
            )

        if ("how long" in q or "period" in q or " n " in f" {q} ") and len(nums) >= 3:
            pv, fv, rate = nums[0], nums[1], _rate_from_percent(nums[2])
            n = solve_n(pv, fv, rate)
            return (
                "**Given:**\n"
                f"- PV = {_money(pv)}\n"
                f"- FV = {_money(fv)}\n"
                f"- i = {rate:.6f}\n\n"
                "**Formula:**\n"
                "n = ln(FV / PV) / ln(1 + i)\n\n"
                "**Substitution:**\n"
                f"n = ln({fv} / {pv}) / ln(1 + {rate:.6f})\n\n"
                "**Final Answer:**\n"
                f"n = **{n:.4f} periods**",
                "solve_n"
            )

        if ("rate" in q or "interest" in q or " i " in f" {q} ") and len(nums) >= 3:
            pv, fv, n = nums[0], nums[1], nums[2]
            i = solve_rate(pv, fv, n)
            return (
                "**Given:**\n"
                f"- PV = {_money(pv)}\n"
                f"- FV = {_money(fv)}\n"
                f"- n = {n}\n\n"
                "**Formula:**\n"
                "i = (FV / PV)^(1/n) - 1\n\n"
                "**Substitution:**\n"
                f"i = ({fv} / {pv})^(1/{n}) - 1\n\n"
                "**Final Answer:**\n"
                f"i = **{i * 100:.4f}%**",
                "solve_rate"
            )

        return (
            "I can solve this TVM question, but I need clear values.\n\n"
            "Example: `Find the present value of ₹10,000 due in 3 years at 8% effective annual interest.`",
            "clarification_required"
        )

    except Exception as e:
        return (
            "**Error:** I could not safely compute this.\n\n"
            f"Reason: `{str(e)}`\n\n"
            "Please check the inputs and try again.",
            "error_handler"
        )
