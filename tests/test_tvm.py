from tools.tvm_tools import (
    present_value,
    future_value,
    solve_rate,
    solve_n,
    nominal_to_effective,
    force_to_effective,
    equation_of_value,
)
from agents.tvm_agent import solve_tvm_query

def test_present_value():
    assert round(present_value(10000, 0.08, 3), 2) == 7938.32

def test_future_value():
    assert round(future_value(5000, 0.06, 4), 2) == 6312.38

def test_solve_rate():
    assert round(solve_rate(1000, 1210, 2), 4) == 0.1000

def test_solve_n():
    assert round(solve_n(1000, 1210, 0.10), 2) == 2.00

def test_nominal_to_effective():
    assert round(nominal_to_effective(0.12, 12), 4) == 0.1268

def test_force_to_effective():
    assert round(force_to_effective(0.05), 4) == 0.0513

def test_equation_of_value():
    cashflows = [
        {"amount": -1000, "time": 0},
        {"amount": 600, "time": 1},
        {"amount": 600, "time": 2},
    ]
    assert round(equation_of_value(cashflows, 0.10, 0), 2) == -4.13

def test_natural_language_monthly_compounding():
    answer, tool = solve_tvm_query("Convert a nominal rate of 12% compounded monthly to an effective annual rate.")
    assert tool == "nominal_to_effective"
    assert "12.6825%" in answer

def test_accumulated_value_wording():
    answer, tool = solve_tvm_query("What is the accumulated value after 5 years of ₹20,000 invested at 7% effective annual interest?")
    assert tool == "future_value"
    assert "₹28,051.03" in answer

def test_solve_rate_wording():
    answer, tool = solve_tvm_query("At what effective annual interest rate will ₹15,000 grow to ₹22,000 in 6 years?")
    assert tool == "solve_rate"
    assert "6.5913%" in answer

def test_how_long_routes_to_n():
    answer, tool = solve_tvm_query("How long will it take ₹5,000 to become ₹10,000 at 9% effective annual interest?")
    assert tool == "solve_n"
    assert "8.0432" in answer

def test_equation_of_value_parsing():
    answer, tool = solve_tvm_query("Find the value at time 2 of cashflows -1000 at time 0, 600 at time 1, and 700 at time 3 using 10% interest.")
    assert tool == "equation_of_value"
    assert "₹86.36" in answer
