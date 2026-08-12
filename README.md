# Two-Tier DevOps Profile — Flask + PostgreSQL

A profile page with **view / edit / update**, built as a **two-tier app**:

- **App tier** — Flask (served by gunicorn), Bootstrap 5 UI
- **Data tier** — PostgreSQL (SQLite fallback for local dev)

Full DevOps setup: unit tests, SonarQube quality gate (SAST), OWASP ZAP
baseline scan (DAST), Docker, Trivy image scanning, Docker Hub publish, and an
EC2 deploy — all via GitHub Actions.

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
├── README.md / SECRETS.md
└── .github/workflows/
    ├── ci-cd.yml                # test ∥ Sonar ∥ ZAP DAST → build → Trivy → push
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

## 🔁 CI/CD pipeline (`ci-cd.yml`)

```
┌── Pytest ──────────────────┐
├── SonarQube + Gate (SAST) ─┼─▶ docker build ─▶ Trivy scan ─▶ docker push
└── OWASP ZAP (DAST) ────────┘     (local load)    (blocks CVE)   (Docker Hub)
   (run in parallel)
```

- **Tests, SonarQube, and ZAP run in parallel** and all must pass.
- **DAST**: the ZAP job boots the real two-tier stack with `docker compose`,
  waits on `/health`, then runs the **ZAP baseline scan** (spider + passive
  rules) against `http://localhost:5000`. The report is uploaded as the
  `zap-baseline-report` artifact. It is **report-only** for now — set
  `fail_action: true` in `ci-cd.yml` to make it a hard gate, and tune
  individual alerts in [.zap/rules.tsv](.zap/rules.tsv).
- The image is built, **scanned by Trivy** (HIGH/CRITICAL), and **only pushed if
  the scan passes** — a vulnerable image never reaches Docker Hub.
- On **pull requests** only the gates run (no build/publish).

## ☁️ EC2 deploy (`deploy-without-docker.yml`)

rsyncs the code to the instance, installs deps into the app's virtualenv, and
restarts the gunicorn systemd service. Nginx (reverse proxy), SSL, PostgreSQL,
the venv, and the systemd unit are provisioned by your server-side scripts.

## 🔐 Secrets

See **[SECRETS.md](SECRETS.md)** for every GitHub secret the workflows need.

## 🧰 Tech stack

Flask · Flask-SQLAlchemy · PostgreSQL · gunicorn · Bootstrap 5 · Docker ·
Docker Compose · GitHub Actions · SonarQube · OWASP ZAP · Trivy · Docker Hub ·
AWS EC2 · Nginx
