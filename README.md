# Agentic Financial Mathematics Solver

A Streamlit Community Cloud app that demonstrates an agentic Financial Mathematics system.

Current active module: TVM Agent.

## Architecture

```text
User
 ↓
Orchestrator Agent
 ├── TVM Agent
 ├── Annuity Agent
 ├── Loan Agent
 ├── Refinance Agent
 └── Bond Agent
```

## Active Concepts

- Present Value
- Future Value / Accumulated Value
- Interest Rate
- Number of Periods
- Nominal to Effective Rate Conversion
- Force of Interest
- Equation of Value

## Run

```bash
python -m streamlit run app.py
```

## Test

```bash
pytest
```
