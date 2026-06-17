# GitHub Actions Secrets

Two workflows ship this app:

- **[ci-cd.yml](.github/workflows/ci-cd.yml)** — Pytest + SonarQube Quality Gate
  → Docker build → Trivy image scan → push to Docker Hub.
- **[deploy-without-docker.yml](.github/workflows/deploy-without-docker.yml)** —
  rsyncs the code to EC2, installs deps into the venv, restarts gunicorn.

Add these under **Settings → Secrets and variables → Actions → New repository
secret**.

## CI/CD pipeline secrets

| Secret name          | Description                                                          | Example                          |
| -------------------- | ------------------------------------------------------------------- | -------------------------------- |
| `DOCKERHUB_USERNAME` | Docker Hub username.                                                 | `bharathcy`                      |
| `DOCKERHUB_TOKEN`    | Docker Hub **access token** (Account Settings → Security).           | `dckr_pat_...`                   |
| `SONAR_TOKEN`        | SonarQube analysis token (My Account → Security → Tokens).           | `sqp_xxx...`                     |
| `SONAR_HOST_URL`     | SonarQube server URL. For SonarQube Cloud use `https://sonarcloud.io`. | `https://sonarqube.example.com` |

## EC2 deploy secrets

| Secret name    | Description                                              | Example                      |
| -------------- | ------------------------------------------------------- | ---------------------------- |
| `EC2_HOST`     | Public IP or DNS of the instance.                       | `13.234.56.78`               |
| `EC2_USER`     | SSH login user.                                         | `ubuntu`                     |
| `EC2_SSH_KEY`  | **Private** SSH key (full PEM contents).                | contents of `your-key.pem`   |
| `APP_DIR`      | Directory on the instance holding the app + its `venv`. | `/opt/two_tire_application`  |
| `SERVICE_NAME` | systemd unit running gunicorn.                          | `two-tire-profile`           |
| `EC2_PORT`     | *(optional)* SSH port if not `22`.                      | `22`                         |

## One-time server preparation (EC2)

The deploy assumes these already exist on the instance (set up by your server
scripts): Python 3, a virtualenv at `$APP_DIR/venv`, PostgreSQL, Nginx reverse
proxy + SSL, and a gunicorn **systemd** unit named `$SERVICE_NAME`. The deploy
user needs passwordless restart of that service:

```bash
echo "$USER ALL=(ALL) NOPASSWD: /bin/systemctl restart two-tire-profile" \
  | sudo tee /etc/sudoers.d/deploy-app
sudo chmod 440 /etc/sudoers.d/deploy-app
```

Example gunicorn systemd unit (`/etc/systemd/system/two-tire-profile.service`):

```ini
[Unit]
Description=Two-tier profile (gunicorn)
After=network.target postgresql.service

[Service]
User=ubuntu
WorkingDirectory=/opt/two_tire_application
Environment="DATABASE_URL=postgresql://profile:profile@localhost:5432/profiledb"
Environment="SECRET_KEY=change-me-in-prod"
ExecStart=/opt/two_tire_application/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 3 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

> Nginx then reverse-proxies `https://<domain>` → `127.0.0.1:5000`.

## Security checklist

- Use a **dedicated deploy user** and a **dedicated SSH key**.
- Store the real `SECRET_KEY` and DB credentials on the server (systemd
  `Environment=` or an env file), **never** in the repo.
- Restrict the EC2 security group so SSH is reachable only from trusted IPs.
