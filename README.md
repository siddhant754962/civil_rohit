# DynamicBuilds Pvt. Ltd.

A full-stack business website for DynamicBuilds Pvt. Ltd., built with FastAPI, Jinja2, SQLAlchemy and PostgreSQL/SQLite.

## Features

- Responsive public pages: home, about, services, projects, contact, privacy and terms.
- Enquiry form with backend validation, safe file uploads, unique reference and database persistence.
- Optional Resend email notifications. Enquiries remain saved if email delivery is unavailable.
- Session-protected admin dashboard, enquiry status/notes management, CSV export and basic project publishing.
- SEO metadata, sitemap, robots.txt and health endpoint.
- Render deployment configuration and PostgreSQL support.

## Local setup (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set a strong unique `SECRET_KEY`. Keep `.env` private.

Create the first admin account interactively:

```powershell
python create_admin.py
```

Start the website:

```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. Admin: http://127.0.0.1:8000/admin/login.

## Email setup

Create a Resend account, verify a sending domain, then set `RESEND_API_KEY` and `EMAIL_FROM` in the environment. Without these settings, enquiries are still saved; email sending is skipped and logged.

## Render deployment

1. Push this folder to a new GitHub repository.
2. In Render, create a Blueprint from the repository and apply `render.yaml`.
3. Set `BASE_URL` to the deployed HTTPS URL.
4. Set `RESEND_API_KEY` and a verified `EMAIL_FROM` value in the Render service environment.
5. Deploy and check `/health`.
6. Create the first admin securely through Render Shell: `python create_admin.py` (interactive shell required).

For production, use a persistent object-storage service for uploads. Render's local filesystem may be ephemeral; local `static/uploads` is suitable for development only. Add a managed persistent disk or S3-compatible storage before relying on uploaded customer files in production.

## Important production notes

- Set a long random `SECRET_KEY`; never commit `.env` or credentials.
- Enable HTTPS and `SECURE_COOKIES=true` in production.
- Configure a verified sender domain with Resend for reliable delivery.
- Configure an external persistent object store for attachments and project images.
- Add Alembic migrations before schema changes; the starter creates tables on startup for initial deployment.
- Add CSRF tokens and a distributed rate limiter (e.g. Redis) before accepting sensitive/high-volume production traffic. The current starter includes same-site session cookies, server validation, a honeypot and in-process admin login throttling, but is not a substitute for a full security audit.
- Add admin UI for content editing and project image upload before representing those management features as complete.
- Structural designs, load calculations and recommendations must be reviewed and approved by appropriately qualified professionals before construction.

## Current scope / known limitations

This is a runnable foundation, not a security-audited production release. Project records can be created, published and deleted from admin, but project image upload and full content editing are not yet implemented. CSRF protection, database migrations, robust distributed rate limiting, attachment access controls, and automated test coverage remain to be completed before a public production launch. Sample homepage imagery is illustrative stock imagery and not company project evidence.
