<div align=center>
	<h1>risk-calculator</h1>
	<a href="https://github.rbx.com/Roblox/grc/actions/workflows/risk-calculator-ci.yml"><img src="https://github.rbx.com/Roblox/grc/actions/workflows/risk-calculator-ci.yml/badge.svg" alt="CI"/></a>
    <div>
        <a href="https://mosaic.rbx.com/service/grc/risk-calculator/deployment"><img height="32" width="32" src="https://cdn.simpleicons.org/roblox" alt="Mosaic"></a>
        &nbsp;
        <a href="ADD RUNBOOK LINK"><img height="32" width="32" src="https://cdn.simpleicons.org/confluence" alt="Runbook"></a>
        &nbsp;
        <a href="https://grafana.rbx.com/d/9821686545468e77d8234e0e32d1d8a0/-managed"><img height="32" width="32" src="https://cdn.simpleicons.org/grafana" alt="Grafana"></a>
        &nbsp;
        
        <a href="ADD JIRA EPIC LINK"><img height="32" width="32" src="https://cdn.simpleicons.org/jira" alt="Jira"></a>
        &nbsp;
        <a href="ADD PAGERDUTY SERVICE LINK"><img height="32" width="32" src="https://cdn.simpleicons.org/pagerduty" alt="PagerDuty"></a>
    </div>
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
