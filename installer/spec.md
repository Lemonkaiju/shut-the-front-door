# Sovereign Family Network — Installer Spec
### Stage 2: Guided Deployment Application

> Version: 0.1 (Draft)
> Last updated: 2026-03-11
> Status: Design / Pre-development

---

## 1. Problem Statement

The technology stack documented in `digital_resistance_guide.md` is effective but requires significant technical knowledge to deploy manually. The target audience — parents and privacy-conscious households — are frequently non-technical. A wall of terminal commands or a failed SSH session causes immediate abandonment.

**The installer must make deployment feel like installing an app, not configuring a server.**

---

## 2. Goals

1. A non-technical parent can complete the full stack deployment with no prior Linux knowledge
2. All sensitive configuration (network details, credentials) stays on the user's machine
3. Setup handles variation between home network configurations gracefully
4. Failures produce human-readable explanations, not raw error output
5. Partial deployments are resumable — the user doesn't start over if something fails

---

## 3. Non-Goals

- This is not a remote SaaS tool — no data is sent to any external service during install
- This does not manage the running infrastructure after setup (that's for OPNsense/AdGuard UIs)
- Not a replacement for the guide — it assumes the user has read Stage 1 first

---

## 4. Deployment Platform

### Host machine (runs the installer)
- **Primary target:** Windows 10/11 (most common parent household OS)
- **Also supported:** Linux (LemonKaijuOS / any distro), macOS
- **Runtime dependency:** Python 3.10+ (or packaged as a standalone `.exe` via PyInstaller so Python is not required)
- **No WSL2 required** — installer uses Python SSH libraries to reach remote targets

### Remote targets (configured by the installer over SSH)
| Target | OS | Role |
|---|---|---|
| VPS | Ubuntu Server 24.04 LTS | WireGuard "Front Door" |
| Edge Device | OPNsense (BSD-based) | Firewall / DNS enforcement |
| Homelab Server | Ubuntu Server 24.04 LTS / Debian 12 | AdGuard, Authentik, Nextcloud |

---

## 5. Interface: Local Web UI

The installer is **not** a terminal application. It runs a local web server, opens the browser automatically, and all user interaction happens in the browser.

```
User launches setup.exe (or python start.py)
        ↓
Local web server starts on http://localhost:3000
        ↓
Browser opens automatically
        ↓
All setup steps happen in a browser UI
        ↓
Terminal is infrastructure only — never the user interface
```

### Web UI principles
- Dark-themed, modern, minimal — feels like a premium app, not a sysadmin tool
- Chat interface for AI assistant (familiar ChatGPT-style UX)
- Progress indicators per step — spinner → green checkmark on success, red X with explanation on failure
- "Show details" toggle collapses raw command output for curious users, hidden by default
- No jargon in primary UI text — all technical terms explained inline on hover or in a sidebar

---

## 6. AI Assistant Module

### Purpose
Handle natural language input, interpret deployment errors, and guide users through the interview process that generates their tailored configuration files.

### Three-tier hardware detection

| Tier | Condition | AI Behaviour |
|---|---|---|
| 1 — GPU | Dedicated GPU detected (NVIDIA/AMD with 6GB+ VRAM) | Ollama + Llama 3.1 8B |
| 2 — CPU-capable | 16GB+ RAM, no GPU or iGPU only | Ollama + Phi-3 Mini 3.8B |
| 3 — Fallback | Under 16GB RAM or user declines AI | Scripted decision-tree wizard, no LLM |

Hardware tier is detected automatically at startup. Tier 3 scripted wizard must be functionally equivalent — the AI is an enhancement, not a dependency.

### Ollama integration
- Ollama is installed locally (Windows native installer available)
- Model is downloaded once and cached
- All inference runs on `localhost` — no data leaves the machine
- The AI is given the following context at runtime:
  - Contents of `network_setup_tracker.md` (current known state)
  - The current deployment step's expected inputs and outputs
  - Any error output from the most recent command

### AI responsibilities
- Conduct the setup interview (network topology, credentials, preferences)
- Generate configuration files from templates based on interview answers
- On failure: read error output, explain in plain English, suggest corrective action
- Update `network_setup_tracker.md` after each successful step
- Never execute commands autonomously — propose actions, user confirms

---

## 7. Setup Interview — Questions the AI Must Ask

Before any deployment begins, the installer collects:

| Question | Used for |
|---|---|
| VPS provider + IP address | SSH target for WireGuard setup |
| VPS SSH key or password | Authentication |
| Home router's current IP | Avoid subnet conflicts in OPNsense |
| Homelab server IP (if exists) | Docker deployment target |
| Family size / number of kid accounts | Authentik + Nextcloud provisioning |
| Preferred domain name (local or public) | Nextcloud + service URLs |
| Which services to deploy (checklist) | Modular deployment — user can skip layers |

All collected values are stored in a local `install_config.json` (never transmitted externally).

---

## 8. Deployment Modules

Each module is independent. Users can deploy any subset. Each module has:
- Pre-flight check (can we reach the target? are dependencies met?)
- Deployment step(s)
- Verification check (did it work?)
- Rollback procedure (undo if verification fails)

### Module 1: WireGuard VPN (VPS)
- Installs Docker on VPS
- Deploys WG-Easy via `docker-compose`
- Generates client configs for home router and family devices
- Verifies tunnel connectivity

### Module 2: OPNsense Configuration
- Imports a pre-generated `config.xml` template (filled from interview answers)
- Configures DNS hijacking rule (port 53 redirect to AdGuard)
- Configures site-to-site tunnel to VPS
- *Note: Requires user to have OPNsense already installed on edge hardware*

### Module 3: AdGuard Home (Homelab)
- Installs Docker + Docker Compose on homelab server if not present
- Deploys AdGuard Home container
- Loads recommended blocklist bundle
- Configures DNS-over-HTTPS upstream resolver

### Module 4: Authentik SSO (Homelab)
- Deploys Authentik via Docker Compose
- Creates parent accounts (with MFA) and child accounts (simplified login)
- Generates OIDC credentials for Nextcloud integration

### Module 5: Nextcloud Hub (Homelab)
- Deploys Nextcloud via Docker
- Connects OIDC to Authentik
- Installs Memories app for local photo AI
- Configures shared family storage

### Module 6: Endpoint Hardening
- Downloads and flashes LemonKaijuOS ISO (links to Git repo)
- Post-install script: installs Brave + LibreWolf via Flatpak, creates child accounts, installs Timekpr-nExT
- *Note: Requires physical access to endpoint device*

---

## 9. State & Resumability

- `install_config.json` — user's interview answers and preferences
- `network_setup_tracker.md` — updated after each successful module completion
- `install_log.json` — timestamped record of every command run and its outcome

If the installer is closed mid-deployment and relaunched, it reads these files to determine which modules are complete and resumes from the next incomplete step.

---

## 10. Distribution

### GitHub Repository
```
sovereign-family-network/
├── README.md
├── guide/
│   └── digital_resistance_guide.md
├── installer/
│   ├── start.py              ← entry point
│   ├── server.py             ← local web server
│   ├── modules/              ← one file per deployment module
│   ├── templates/            ← config templates (docker-compose, config.xml, etc.)
│   ├── ai/                   ← Ollama integration layer
│   └── web/                  ← browser UI (HTML/CSS/JS)
├── dist/
│   └── setup.exe             ← packaged Windows executable (GitHub Release)
└── network_setup_tracker.md  ← user's local state (gitignored after clone)
```

### GitHub Pages
- Auto-built from `guide/` directory
- Serves the digital resistance guide as a readable website
- Free hosting, updates automatically on push
- Links to GitHub Release for installer download

---

## 11. Out of Scope for Stage 2 (Future Stages)

- Mobile device configuration (iOS/Android DNS + VPN profiles)
- Ongoing monitoring dashboard
- Remote management after initial deployment
- Multi-household / community deployment tooling

---

## 12. Open Questions

- [ ] Which LLM model gives the best quality/size tradeoff for Tier 2 CPU path — Phi-3 Mini vs Llama 3.2 3B?
- [ ] Should OPNsense module target the REST API or config.xml import? (REST API is cleaner but requires OPNsense to be reachable first)
- [ ] Legal/disclaimer requirements for Australian context — age verification bypass implications
- [ ] Should the GitHub repo be under a personal account or a new org? (Org preferred for community credibility)
