<div align=center>
	<h1>risk-calculator</h1>
</div>

## About

A Python implementation of the Open FAIR (Factor Analysis of Information Risk) framework using Monte Carlo simulation for quantitative risk analysis.

**Risk Taxonomy:**
- Risk = LEF × LM
- LEF = TEF × Vulnerability (or CF × PoA → TEF)
- LM = Primary Loss + Secondary Loss (SLEF × SLM)

## Getting Started

- Build and run: `make run`
- Unit test: `make test`
- Test with coverage: `make test-cov`
- Lint: `make lint`
- Clean: `make clean`

## Local Development (without Docker)

```bash
cd services/risk-calculator
pip install -r src/requirements.txt
pip install pytest pytest-cov
PYTHONPATH=. python -m webapp.app
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Web UI for the calculator |
| `/api/simulate` | POST | Run ALE Monte Carlo simulation |
| `/api/simulate-sle` | POST | Run single loss event simulation |
| `/api/vulnerability` | POST | Calculate vulnerability (21x21 grid) |
| `/api/compare` | POST | Compare two scenarios |
| `/api/scenarios` | GET/POST | List or create scenarios |
| `/api/scenarios/:id` | GET/PUT/DELETE | Manage a specific scenario |
