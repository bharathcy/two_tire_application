# Two-Tier DevOps Profile — Flask + PostgreSQL

A profile page with **view / edit / update**, built as a **two-tier app**:

- **App tier** — Flask (served by gunicorn), Bootstrap 5 UI
- **Data tier** — PostgreSQL (SQLite fallback for local dev)

Full **DevSecOps pipeline**: secrets scanning, unit tests, dependency audit
(SCA), SAST, IaC scanning, DAST, image scanning + SBOM, and simulated
deploy/monitoring stages — all via GitHub Actions. Stages that need real
infrastructure or credentials run in **simulation mode** and explain what they
would do.

## 📁 Project structure

```
two_tire_application/
├── app/
│   ├── __init__.py            # App factory (DB config, blueprint, seed)
│   ├── models.py              # Profile model + seed data
│   ├── routes.py              # / (view), /edit (edit+update), /health
│   ├── templates/             # base / index / edit (Jinja)
│   └── static/style.css       # Styling
├── tests/test_app.py          # Pytest: health, view, edit/update
├── wsgi.py                    # gunicorn entrypoint
├── requirements.txt           # Runtime deps
├── requirements-dev.txt       # + pytest
├── Dockerfile                 # python:3.12-slim + gunicorn
├── docker-compose.yml         # web + db (the two tiers)
├── sonar-project.properties   # SonarQube config
├── .zap/rules.tsv             # OWASP ZAP (DAST) alert tuning
├── .gitleaks.toml             # Gitleaks (secrets scan) allowlist
├── README.md / SECRETS.md
└── .github/workflows/
    ├── ci-cd.yml                # sequential DevSecOps chain (see below)
    └── deploy-without-docker.yml # rsync code → venv install → restart gunicorn
```

## 🚀 Run locally

### Option A — Docker Compose (both tiers)

```bash
docker compose up --build
# app on http://localhost:5000  (Postgres runs alongside)
```

### Option B — Flask only (SQLite, no Postgres)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python wsgi.py            # http://localhost:5000
pytest -q                # run the tests
```

## 🧭 Routes

| Route     | Method   | Purpose                          |
| --------- | -------- | -------------------------------- |
| `/`       | GET      | View the profile                 |
| `/edit`   | GET/POST | Edit form / save the update      |
| `/health` | GET      | Health probe (`{"status":"ok"}`) |

## 🔁 DevSecOps pipeline (`ci-cd.yml`)

Eleven sequential stages — each is a gate, a failure stops the chain:

```
Secrets Scan ─▶ Pytest ─▶ SCA ─▶ SAST ─▶ IaC Scan ─▶ DAST
  (Gitleaks)             (pip-audit) (Bandit+Sonar) (Trivy)  (OWASP ZAP)
     ─▶ Build+Trivy+SBOM+Push* ─▶ Staging* ─▶ Smoke Test* ─▶ Production* ─▶ Monitoring*
                                          (* simulated where infra/creds are absent)
```

### Security stages explained

| # | Stage | Tool | What it protects against | Mode |
|---|-------|------|--------------------------|------|
| 1 | Secrets scan | Gitleaks | Credentials leaked into code or **git history** — exploitable forever once pushed | ✅ real |
| 2 | Unit tests | Pytest | Regressions; the basic correctness gate | ✅ real |
| 3 | SCA | pip-audit | Known CVEs in **dependencies** (how most breaches start, e.g. Log4Shell) | ✅ real |
| 4 | SAST | Bandit + SonarQube | Insecure **code patterns**: injection risks, `debug=True`, weak crypto | ✅ real |
| 5 | IaC scan | Trivy config | **Misconfigured infrastructure**: root containers, exposed services | ✅ real |
| 6 | DAST | OWASP ZAP | Vulnerabilities visible only in the **running app**: missing headers, CSRF, error leakage | ✅ real |
| 7 | Image scan + SBOM | Trivy | CVEs in the **shipped image**; SBOM = supply-chain transparency. Signing (Cosign) simulated | ✅ real / 🔸 sign+push sim |
| 8 | Staging deploy | — | Verifying the exact scanned artifact in a prod-like env (blue/green) | 🔸 simulated |
| 9 | Smoke test | — | Broken deploys, missing TLS/security headers, before promotion | 🔸 simulated |
| 10 | Production deploy | — | Approval gates (four-eyes), build-once-promote-many, canary + rollback | 🔸 simulated |
| 11 | Monitoring | Prometheus/Falco/WAF | **Detection & response** after ship: attacks, new CVEs, outages | 🔸 simulated |

Notes:

- **DAST** boots the real two-tier stack with `docker compose`, waits on
  `/health`, then runs the ZAP baseline scan against `http://localhost:5000`.
  Report: `zap-baseline-report` artifact. Report-only for now — set
  `fail_action: true` to make it blocking; tune alerts in
  [.zap/rules.tsv](.zap/rules.tsv).
- **Simulation mode** (stages marked 🔸) activates automatically when
  credentials/infrastructure are absent, logs exactly what a real stage would
  do, and writes an explainer to the job's **Summary** page. Adding the Docker
  Hub secrets flips the push from simulated to real with no workflow change.
- The simulated stages write their explanation to the run's **Summary** tab —
  open any run and read the stage-by-stage security narrative.
- On **pull requests** only the scan gates run (no build/publish/deploy).
- These scans have already caught real issues in this repo: a root-running
  Dockerfile (fixed with a non-root `USER`), hardcoded `debug=True` (now env
  driven), and CVEs in gunicorn 22.0.0, Flask 3.0.3, python-dotenv 1.0.1
  (all bumped).

## ☁️ EC2 deploy (`deploy-without-docker.yml`)

rsyncs the code to the instance, installs deps into the app's virtualenv, and
restarts the gunicorn systemd service. Nginx (reverse proxy), SSL, PostgreSQL,
the venv, and the systemd unit are provisioned by your server-side scripts.

## 🔐 Secrets

See **[SECRETS.md](SECRETS.md)** for every GitHub secret the workflows need.

## 🧰 Tech stack

Flask · Flask-SQLAlchemy · PostgreSQL · gunicorn · Bootstrap 5 · Docker ·
Docker Compose · GitHub Actions · Gitleaks · pip-audit · Bandit · SonarQube ·
Trivy · OWASP ZAP · Docker Hub · AWS EC2 · Nginx
