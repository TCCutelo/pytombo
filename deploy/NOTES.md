# Deployment notes

## Server

- Hetzner CX22, Ubuntu 24.04 (shared box, also hosts memi, filias.dev, etc.)
- IP: 46.224.236.207
- Domain: tombo.filias.dev
- SSH key: ~/.ssh/memi

## SSH in

```
ssh -i ~/.ssh/memi root@46.224.236.207
```

## Architecture

```
Internet → Caddy (:443, auto HTTPS) → Streamlit (:8501) → app.py
                                     → webhook (:9011) on /deploy
```

Ports on this shared server: app = 8501, webhook = 9011.

## Deploy updates

Auto-deploys on push to main via GitHub webhook (https://tombo.filias.dev/deploy).

Manual deploy if needed:

```
ssh -i ~/.ssh/memi root@46.224.236.207
cd /opt/pytombo && sudo -u pytombo -H git pull && sudo -u pytombo -H uv sync && systemctl restart pytombo
```

## Useful commands (on the server)

```bash
systemctl status pytombo            # app status
journalctl -u pytombo -f            # follow app logs
systemctl restart pytombo           # restart app
systemctl status pytombo-webhook    # webhook status
journalctl -u pytombo-webhook -f    # follow webhook logs
```

## Config files on server

- /opt/pytombo/ — app code (cloned, owned by user `pytombo`)
- /etc/caddy/Caddyfile — reverse proxy (shared; tombo.filias.dev block appended)
- /etc/systemd/system/pytombo.service — app service
- /etc/systemd/system/pytombo-webhook.service — webhook service (holds WEBHOOK_SECRET)

## Optional: OCR backends

The Streamlit app runs the text tab out of the box. To enable the image tabs:

- OpenAI backend: set `OPENAI_API_KEY` (add an `Environment=` line to
  pytombo.service, then `systemctl daemon-reload && systemctl restart pytombo`).
- Tesseract backend: `apt-get install -y tesseract-ocr tesseract-ocr-por`.

## Fresh setup (if starting over)

1. As root: create user, clone, sync deps

   ```bash
   useradd --system --create-home --shell /usr/sbin/nologin pytombo
   install -d -o pytombo -g pytombo /opt/pytombo
   sudo -u pytombo -H git clone https://github.com/TCCutelo/pytombo.git /opt/pytombo
   git config --global --add safe.directory /opt/pytombo
   cd /opt/pytombo && sudo -u pytombo -H uv sync
   ```

2. Install services (inject a real secret into the webhook service)

   ```bash
   SECRET=$(openssl rand -hex 20)
   cp deploy/pytombo.service /etc/systemd/system/
   sed "s/CHANGE_ME/$SECRET/" deploy/pytombo-webhook.service > /etc/systemd/system/pytombo-webhook.service
   systemctl daemon-reload
   systemctl enable --now pytombo pytombo-webhook
   ```

3. Append the `deploy/Caddyfile.snippet` block to `/etc/caddy/Caddyfile`, then
   `caddy validate --config /etc/caddy/Caddyfile && systemctl reload caddy`.

4. DNS: point an A record for `tombo.filias.dev` at `46.224.236.207`.

5. GitHub → repo Settings → Webhooks → Add webhook:
   - Payload URL: `https://tombo.filias.dev/deploy`
   - Content type: `application/json`
   - Secret: the `$SECRET` from step 2
   - Events: Just the push event
