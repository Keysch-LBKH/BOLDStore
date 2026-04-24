# SOP-N8N-001: Domain Reconfiguration

**SOP ID:** SOP-N8N-001
**Category:** N8N
**Version:** 1.0.0
**Last Reviewed:** 2026-04-24
**Owner:** LBKH Solutions
**Estimated Time:** 15 minutes

---

## Purpose

Reconfigure N8N's domain when the existing domain expires or changes.

## Scope

Performed by a sysadmin when the N8N subdomain needs to change.

## Prerequisites

- [ ] SSH/console access to the N8N server (`128.199.12.191`)
- [ ] New domain DNS access (Cloudflare)
- [ ] New domain decided (e.g. `n8n.lbkh.solutions`)

---

## Server Details

| Item | Value |
|---|---|
| Server IP | `128.199.12.191` |
| OS | Ubuntu 22.04 LTS (DigitalOcean SFO3) |
| N8N Version | 2.0.3 |
| Compose file | `/opt/n8n-docker-caddy/docker-compose.yml` |
| Env file | `/opt/n8n-docker-caddy/.env` |
| Nginx config | `/etc/nginx/sites-available/reverse-proxy.conf` |
| SSL managed by | Certbot + Let's Encrypt |
| Reverse proxy | Nginx (ports 80/443) → N8N (port 5678) |
| Note | Caddy runs in Docker (ports 8080/8443) but is NOT in the traffic path — Nginx handles all SSL and proxying directly to N8N |

## Procedure

### Step 1 — Add DNS A record (Cloudflare)

In Cloudflare for `lbkh.solutions`:
- **Type:** A
- **Name:** `n8n` (or desired subdomain)
- **Value:** `128.199.12.191`
- **TTL:** 300
- **Proxy:** OFF (grey cloud — DNS only)

### Step 2 — Update server config files

```bash
# Update .env
sed -i 's/DOMAIN_NAME=OLD_DOMAIN/DOMAIN_NAME=NEW_DOMAIN/' /opt/n8n-docker-caddy/.env
sed -i 's/N8N_HOST=OLD_HOST/N8N_HOST=NEW_HOST/' /opt/n8n-docker-caddy/.env
sed -i 's|WEBHOOK_URL=https://OLD_HOST/|WEBHOOK_URL=https://NEW_HOST/|' /opt/n8n-docker-caddy/.env

# Update Caddyfile (not in traffic path but keep in sync)
sed -i 's/OLD_HOST/NEW_HOST/' /opt/n8n-docker-caddy/caddy_config/Caddyfile

# Update Nginx config
sed -i 's/OLD_HOST/NEW_HOST/g' /etc/nginx/sites-available/reverse-proxy.conf
sed -i 's|letsencrypt/live/OLD_HOST|letsencrypt/live/NEW_HOST|g' /etc/nginx/sites-available/reverse-proxy.conf
```

### Step 3 — Get new SSL certificate

```bash
certbot certonly --nginx -d NEW_HOST
# If certbot path has -0001 suffix, strip it:
sed -i 's|NEW_HOST-0001|NEW_HOST|g' /etc/nginx/sites-available/reverse-proxy.conf
```

### Step 4 — Restart N8N stack

```bash
cd /opt/n8n-docker-caddy && docker compose down && docker compose up -d
```

### Step 5 — Reload Nginx

```bash
nginx -t && systemctl reload nginx
```

### Step 6 — Add X-Forwarded-Host header (if not present)

```bash
grep -q "X-Forwarded-Host" /etc/nginx/sites-available/reverse-proxy.conf || \
  sed -i '/proxy_set_header X-Forwarded-Proto/a\    proxy_set_header X-Forwarded-Host $host;' \
  /etc/nginx/sites-available/reverse-proxy.conf
nginx -t && systemctl reload nginx
```

---

## Verification

- [ ] `https://NEW_HOST` loads N8N login page in browser
- [ ] `curl http://127.0.0.1:5678/api/v1/workflows` returns JSON (test from server)
- [ ] N8N webhook URLs updated in all active workflows

## Notes

- N8N API cannot be called externally from Claude Code sandbox (Anthropic TLS inspection proxy blocks it). Always run N8N API calls via `curl` from the server console using `source /opt/n8n-docker-caddy/.env` to load the API key.
- All BOLDStore workflows must have the `BOLDStore` tag applied (ID: `akucO9y04icJCSvB`)

---

## Changelog

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-04-24 | LBKH | Initial — documented during boldlogic.io → lbkh.solutions migration |
