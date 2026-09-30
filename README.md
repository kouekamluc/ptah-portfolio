# Ptah Kouekam Kamgou Luc Kevin &mdash; Engineering & Software Portfolio Platform

> **"Engineer. Developer. Builder."**  
> A production-grade, server-rendered digital identity platform designed for mechatronics engineering, embedded systems, electronics, control systems, and robust web software.

[![Django](https://img.shields.io/badge/Django-5.2+-092e20?style=flat&logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13+-3776ab?style=flat&logo=python)](https://www.python.org/)
[![HTMX](https://img.shields.io/badge/HTMX-1.9+-3366cc?style=flat)](https://htmx.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4+-06b6d4?style=flat&logo=tailwindcss)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 1. System Architecture

The platform prioritizes **progressive enhancement, minimal client-side overhead, sub-100ms response times, and comprehensive database configurability**. It rejects bloated Single-Page Application (SPA) frameworks in favor of clean Django Server-Side Rendering (SSR) augmented with HTMX.

```
                    ┌──────────────────────────────────────────────┐
                    │            Browser Client                    │
                    │   (Semantic HTML5 + Tailwind CSS)            │
                    └───────┬──────────────────────────────▲───────┘
                            │                              │
                     HTTP / HTMX                    HTML Fragment /
                       Requests                     Full Document
                            │                              │
                            ▼                              │
                    ┌──────────────────────────────────────────────┐
                    │      WhiteNoise / Reverse Proxy (Gunicorn)   │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │             Django Core Kernel               │
                    ├──────────────┬───────────────┬───────────────┤
                    │ core         │ projects      │ notes         │
                    │ - Settings   │ - Case Studies│ - Lab Logs    │
                    │ - Stack      │ - Specs / BOM │ - Safe MD     │
                    │ - Timeline   │ - Hardware DAQ│ - Reading Time│
                    ├──────────────┴───────────────┴───────────────┤
                    │ contact                                      │
                    │ - Anti-Spam Honeypot                         │
                    │ - Validated Inquiries                        │
                    └──────────────────────┬───────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │      Database: PostgreSQL (Prod) / SQLite    │
                    └──────────────────────────────────────────────┘
```

---

## 2. Key Engineering Highlights

- **Flexible Identity Architecture**: Full name (*Ptah Kouekam Kamgou Luc Kevin*), titles, bios, location, and availability indicators are managed dynamically in Django Admin via a Singleton model, avoiding brittle hardcoded strings in templates.
- **Multidisciplinary Engineering Support**: Full case studies accommodate physical systems (ESP32, Arduino, opamps, active filters, control loops, sensors) alongside web applications. Includes quantitative engineering metric grids (e.g., *1.0 kHz Loop Rate*, *16-bit ADC*, *88.4 dB CMRR*).
- **Graceful CV Routing**: Dedicated `/cv/` permalink dynamically serves the active uploaded resume version (`resume_file`), or gracefully falls back to a contact inquiry modal if a new revision is being prepared.
- **Health Check & Telemetry (`/health/`)**: Dedicated JSON health endpoint checking database connectivity and returning `{"status": "healthy", "database": "connected"}` for uptime monitors and Railway deploy checks.
- **Contact Security & Rate Limiting**: Anti-spam honeypot plus session-based rate limiting (max 3 submissions / 5 minutes) preventing automated abuse while preserving full accessible fallback without JavaScript.
- **Zero-Flicker Dark / Light Themes**: Integrated script in `<head>` queries `localStorage` and OS preferences prior to CSS rendering, eliminating dark-mode flash.
- **Accessible Command Palette (`Ctrl+K` / `Cmd+K`)**: Keyboard-driven modal providing immediate navigation across projects, hardware showcases, notes, and live search.
- **Progressive HTMX Layer**: Project filtering, pagination, search, and contact submissions dynamically swap partial DOM nodes without page reloads, while retaining 100% functionality when JavaScript is disabled.
- **Secure Markdown Processing**: Engineering lab notes support code blocks, equations, and tables safely sanitized via Bleach before rendering.

---

## 3. Directory Layout

```
├── core/                       # Global identity, stack, timeline, education & search
│   ├── management/commands/    # Database seeding commands (seed_portfolio.py)
│   ├── context_processors.py   # Global context injection (settings, socials)
│   ├── models.py               # SiteSettings, Technology, Education, Timeline
│   ├── sitemaps.py             # XML sitemap generator
│   └── views.py                # Home, About, Stack, Search, Health, CV Download, Robots
├── projects/                   # Engineering & software project showcase
│   ├── models.py               # Project, ProjectMetric, ProjectImage, ProjectFile
│   ├── urls_engineering.py    # Dedicated /engineering/ route
│   └── views.py                # List (with HTMX filter), Engineering, Detail
├── notes/                      # Technical writing, lab logs, tutorials
│   ├── models.py               # Note, NoteCategory (Bleach sanitized Markdown)
│   └── views.py                # Note list and case study views
├── contact/                    # Public inquiries and communication
│   ├── forms.py                # Honeypot-enabled ContactForm
│   ├── models.py               # ContactMessage
│   └── views.py                # Dual standard/HTMX submission handler with rate limiting
├── portfolio_site/             # Project configuration package
│   ├── settings/
│   │   ├── base.py             # Shared settings
│   │   ├── development.py      # Local development overrides
│   │   └── production.py       # Hardened SSL/HSTS production configuration
│   ├── urls.py                 # Root routing table
│   └── wsgi.py                 # Production WSGI entry point
├── static/                     # Compiled CSS, vendor JS (HTMX, Alpine), and assets
├── templates/                  # Modular HTML5 Django templates
├── Dockerfile                  # Production container definition
├── docker-compose.yml          # Containerized web + PostgreSQL stack
├── Procfile                    # Railway / PaaS process declaration
├── runtime.txt                 # Exact Python runtime version (3.13.2)
└── requirements.txt            # Python dependencies
```

---

## 4. Local Installation & Quickstart

### Prerequisites
- Python 3.13+
- Node.js 18+ (for compiling Tailwind CSS, optional if using pre-compiled `static/css/styles.css`)

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/YOUR_USERNAME/ptah-portfolio.git
cd ptah-portfolio

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Defaults in `.env` are configured for immediate local SQLite execution)*.

### 4. Run Migrations & Seed Database
```bash
python manage.py migrate
python manage.py seed_portfolio
```
The `seed_portfolio` command populates Ptah Kouekam's complete profile, realistic software & engineering projects, technical stack, academic education in Italy, and sample notes.

### 5. Create Administrative Superuser
```bash
python manage.py createsuperuser
```
*(Or use pre-configured local development credentials: username `ptahkouekam`, password `kklkinkklk`)*.

### 6. Compile Tailwind CSS (Optional)
```bash
npm install
npm run build:css
```
To watch for CSS changes during active editing:
```bash
npm run watch:css
```

### 7. Start Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 5. Automated Testing & Verification

Run the comprehensive test suite (24 tests covering models, singletons, views, HTMX partial swaps, markdown sanitization, health check, CV fallback, and contact honeypot/rate limiting):

```bash
python manage.py test
```

Run deployment readiness check against production settings:
```bash
python manage.py check --deploy --settings=portfolio_site.settings.production
```

---

## 6. Django Administration (CMS)

Access the administration dashboard at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

The admin interface acts as a personal CMS allowing you to:
1. **Site Settings**: Modify full name, professional positioning, short/long bio, upload new CV PDFs, and toggle availability status.
2. **Projects**: Add engineering or software projects with inline metrics, schematics, CAD files, and bill of materials.
3. **Technologies**: Maintain the tech stack categorized by domain with proficiency levels.
4. **Currently Building**: Update the real-time workbench banner on the homepage with progress percentages.
5. **Technical Notes**: Author lab notes in Markdown with automatic reading time calculation and sanitized rendering.
6. **Inquiries**: Review messages sent through the contact form.

---

## 7. Railway & Production Deployment

### Recommended: Deploying to Railway

1. **Create Project**: Connect your GitHub repository to Railway.
2. **Add PostgreSQL Service**: Add a Railway PostgreSQL database. Railway automatically provisions and links `DATABASE_URL`.
3. **Set Environment Variables**:
   - `DJANGO_SETTINGS_MODULE`: `portfolio_site.settings.production`
   - `SECRET_KEY`: A cryptographically secure random string (minimum 50 characters).
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.railway.app,yourdomain.com`
   - `CSRF_TRUSTED_ORIGINS`: `https://*.railway.app,https://yourdomain.com`
4. **Build & Start**:
   - The repository includes a `Procfile` (`web: gunicorn portfolio_site.wsgi:application --bind 0.0.0.0:$PORT`) and `runtime.txt`.
   - Set Build Command (or Railway Pre-deploy command):
     ```bash
     python manage.py collectstatic --noinput && python manage.py migrate
     ```
5. **Health Check Path**: Set Railway health check path to `/health/`.

### Alternative: Docker Compose (Self-Hosted VPS)
```bash
docker-compose up -d --build
```
This launches a PostgreSQL container and a Gunicorn WSGI container with automated static asset collection via WhiteNoise.

---

## 8. Deployment Verification Checklist

- [ ] `DEBUG=False` set in production environment
- [ ] Unique, secure `SECRET_KEY` set (50+ random characters)
- [ ] `ALLOWED_HOSTS` configured for production domain
- [ ] `CSRF_TRUSTED_ORIGINS` configured for HTTPS domain
- [ ] PostgreSQL connected via `DATABASE_URL`
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] WhiteNoise serving minified CSS/JS and assets
- [ ] Health check endpoint (`/health/`) returns 200 OK
- [ ] Admin panel accessible (`/admin/`) with initial superuser
- [ ] Homepage hero, workbench, and project previews display properly
- [ ] CV button links to active PDF or falls back to inquiry modal
- [ ] Contact form validates, blocks honeypot spam, and enforces rate limit
- [ ] 404, 403, and 500 custom error pages render branded layout
- [ ] Automated test suite passes 100% (`python manage.py test`)

---

## 8. License & Credits

Designed and engineered by **Ptah Kouekam Kamgou Luc Kevin**.  
Open-source under the [MIT License](LICENSE).
