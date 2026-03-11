# The Digital Resistance Field Guide
### A parent's handbook for taking back control of your family's online life

> *"The internet was built to survive a nuclear war. Your data shouldn't be less resilient than that."*

---

## Who this is for

You don't need to be a network engineer. You need to be a parent — or just someone who's had enough.

This guide is written for people who are tired of:
- Their kids' every click being sold to advertisers
- Age-verification laws that demand government ID to watch YouTube
- "Parental controls" that live in someone else's cloud and report back to them
- Smart devices that spy on your home
- Phones and laptops that phone home to corporate servers constantly

This is the system we built for our own family. It's real, it works, and we're sharing every step.

---

## The honest truth up front

This is not a one-click solution. **Stage 1** of this guide explains *what* to build and *why*. **Stage 2** (coming soon) provides automation scripts and guided installers that make deployment much less scary. 

You don't have to do everything at once. Even implementing one layer — say, just the DNS sinkhole — gives your family meaningful protection immediately.

---

## Why should you trust this?

If you're trying to escape companies tracking your family, why should you trust the tools in this guide? It's a fair question. 

1. **We don't sell anything.** There are no premium tiers, no subscriptions, and no hidden fees in this project. 
2. **Nothing leaves your house.** The core principle of this setup is that *you* own the servers. The accounts, the parental controls, and the AI assistants all run locally on your own hardware. We don't have a cloud for your data to go to.
3. **Everything is public, open-source, and auditable.** Every piece of software recommended here (from AdGuard to Bazzite to the deployment tools we wrote) is open-source. That means the code is public and constantly audited by security researchers worldwide. There are no secret backdoors.
4. **We are just parents.** This project wasn't built by a tech startup trying to acquire users. It was built by a family trying to solve this exact problem for their own kids, and sharing the homework so you don't have to start from scratch.

---

## The Threat Model — What are we actually defending against?

Before setting up anything, it helps to know what you're protecting against. Here's what a normal unprotected home network looks like from the outside:

| Threat | How it works | What it can do |
|---|---|---|
| **ISP surveillance** | Your ISP sees every domain you visit by default | Sells browsing data to data brokers, hands to government on request |
| **DNS leakage** | Your device asks "where is google.com?" in plain text | ISPs and network-level observers log every site lookup |
| **Corporate telemetry** | Windows, Android, smart TVs send usage data constantly | Builds a persistent profile of your household's behaviour |
| **Ad network tracking** | Cookies, fingerprinting, pixel trackers | Follows your family across every website they visit |
| **Age-verification laws (AU)** | Sites must verify age by region/IP | Forces users to hand over ID or be blocked |
| **Smart device snooping** | IoT devices (TVs, speakers, cameras) phone home | Audio/visual data sent to vendor servers, sometimes third parties |

---

## The Stack — Our actual setup

We use a layered approach. Each layer adds protection independently. Together, they form a "defence in depth" — even if one layer is bypassed, others still hold.

```
[ Internet ]
      |
[ VPS "Front Door" — WireGuard ]   ← masks your home IP, bypasses regional blocks
      |
[ OPNsense Edge Firewall ]          ← controls all traffic in/out of your home
      |
[ AdGuard Home — DNS Sinkhole ]     ← kills ads, trackers & malware at the DNS level
      |
[ Authentik — Identity Provider ]   ← one login for your whole family, no Google/Microsoft
      |
[ Nextcloud — Private Cloud ]       ← your photos, docs, calendar. No surveillance
      |
[ LemonKaijuOS Endpoints ]          ← hardened OS on every family device
```

---

## Layer 1: The Front Door — Your VPS & VPN

### What problem does this solve?

Your home internet connection has a public IP address. Anyone — your ISP, a government agency, a website — can trace activity back to your household. Age-verification systems in Australia and other regions use this IP to block or demand ID.

A VPS (Virtual Private Server) is a small rented computer in another country. You route your traffic through it like a relay. The website sees the VPS's IP, not yours.

### Why WireGuard?

WireGuard is a modern VPN protocol. It's:
- **Fast** — runs in the OS kernel, not user-space
- **Auditable** — only ~4,000 lines of code (OpenVPN is ~600,000)
- **Simple** — a fraction of the configuration complexity of older protocols

### What you'll need

- A rented VPS (we recommend **Kamatera** for flexibility or **Hostinger** for budget ~$5/month)
- About 45 minutes

### Beginner path
> **Stage 2 of this guide will provide a single script** that SSHs into your new VPS and configures WireGuard automatically. For now, we recommend WG-Easy: a one-command Docker deployment with a browser-based web UI.

### Power user path
Consider **NetBird** if you want a full zero-trust mesh network that integrates with Authentik (your identity provider) so every device on your network is authenticated.

---

## Layer 2: The Edge Firewall — OPNsense

### What problem does this solve?

A consumer router (the thing your ISP gave you) does the bare minimum. OPNsense is a professional-grade open-source firewall that runs on a small dedicated mini-PC and gives you full control over:
- Which devices can talk to what
- Intercepting DNS bypass attempts by smart TVs and hardcoded apps
- VPN routing for specific devices or the whole household

### Why OPNsense over pfSense?
OPNsense is maintained more actively, has a cleaner UI, and has better plugin support for modern privacy tools.

### What you'll need
- A mini-PC with at least two network ports (NICs). Look for Intel i225 or i226 based NICs — they have excellent driver support.
- Around 2-4 hours for initial setup

### Key config: DNS Hijacking
Many smart TVs and apps are hardcoded to use Google's DNS (`8.8.8.8`) specifically to bypass parental controls and ad blockers. OPNsense lets you intercept all outbound DNS requests (port 53) and redirect them to your AdGuard Home server — so there's no escape.

---

## Layer 3: DNS Sinkhole — AdGuard Home

### What problem does this solve?

Every time your device wants to load a webpage, it first asks a DNS server "what's the IP address for this domain?" A DNS sinkhole intercepts those requests and returns nothing for known ad, tracker, and malware domains — so the connection never happens at all.

This is the single highest-value thing you can do for a home network. It works for **every device** — phones, tablets, smart TVs, game consoles — without installing anything on them.

### Why AdGuard Home over Pi-hole?
Both are excellent. We chose AdGuard Home because:
- It has **built-in parental controls** (safe search enforcement, content categories)
- It supports **encrypted DNS** (DNS-over-HTTPS and DNS-over-TLS) out of the box
- Pi-hole needs third-party add-ons (like Unbound) to achieve the same result

### What you'll need
- Your homelab server (or even a Raspberry Pi 4)
- Docker installed
- About 20 minutes

> **Stage 2** will include a pre-configured `docker-compose.yml` with recommended blocklists already loaded.

---

## Layer 4: Sovereign Identity — Authentik SSO

### What problem does this solve?

Every account your family creates with Google, Apple, or Microsoft is a permanent data collection point. These companies build detailed profiles from login activity, cross-device tracking, and usage patterns.

Authentik is a self-hosted identity provider. It gives your family one central login (like "Sign in with Google" — except it's your server). You control:
- Who can log in and to what
- MFA requirements (adults get strict MFA, kids get simplified login)
- Access logs — you can see exactly who logged in, when, and where

### What you'll need
- Your homelab server
- Docker Compose
- About 1-2 hours

---

## Layer 5: Private Cloud — Nextcloud Hub

### What problem does this solve?

Google Drive, Google Photos, iCloud, and OneDrive are convenient. They are also comprehensive surveillance platforms. Google's terms explicitly allow them to scan your photos and documents.

Nextcloud is a self-hosted replacement that provides:
- File sync and sharing (like Google Drive)
- Photo library with **local, on-device AI** for face/object recognition — your faces never leave your server
- Calendar and contacts (replace Google Calendar)
- Office document editing (replace Google Docs)

### What you'll need
- Your homelab server (the more storage the better — plan for your whole family's photo library)
- Docker
- About 1 hour setup, ongoing storage growth

---

## "But what do we use instead of Google Docs?"

The biggest fear when moving away from Big Tech is losing the tools you rely on. The reality is that open-source alternatives have caught up, and in many cases, they're better (and free). 

Here is what giving up your subscriptions actually looks like:

| What you have | What you get | The bonus |
|---|---|---|
| Google Drive / OneDrive | **Nextcloud Files** | No storage limits other than your own hard drives. |
| Google Photos / iCloud | **Nextcloud Memories** | AI face/object recognition runs locally. Your photos never leave your house. |
| Google Docs / Office 365 | **LibreOffice** (offline) or **Nextcloud Office** | Save the $100+ yearly Microsoft 365 subscription. |
| Google Calendar / Contacts | **Nextcloud Calendar/Contacts** | Syncs perfectly to your iPhone or Android natively via CalDAV/CardDAV. |
| Adobe Acrobat ($20/mo) | **Okular** or Firefox/Brave built-in | Free, offline PDF editing and signing by default. |
| 1Password / LastPass | **Bitwarden** (self-hosted) | Enterprise-grade password management without the cloud targets. |
| Chrome / Edge | **Brave** | Identical day-to-day feel, but blocks trackers and ads out of the box. |
| Windows / Mac OS | **Bazzite / Linux Mint** | Free, no telemetry, no forced AI features, no ads in your start menu. |

*Note: For the extremely rare Windows app that has no Linux equivalent, tools like **WinApps** let you run a contained Windows virtual machine where the app appears in a normal window on your Linux desktop — fully isolated from your real files and network.*

### The App Security Tiers

You do not have to be an absolutist. "Fully self-hosted or nothing" is a standard most families will fail. 

You can mix and match based on this security tiering:

- 🟢 **Tier 1: Fully sovereign (Best).** You use local apps (LibreOffice) and self-hosted services (Nextcloud). Zero corporate cloud involvement. Use this for your personal files, family photos, and passwords.
- 🟡 **Tier 2: Browser-contained (Good compromise).** You still use Google Docs or Office 365 for school/work, but *only* inside a hardened browser (Brave/LibreWolf). The service knows you used it, but it cannot read your local files, cannot install background agents, and your DNS sinkhole still blocks their trackers.
- 🔴 **Tier 3: Native App (Not recommended).** Installing Chrome, Teams, or Office directly on your machine. This gives them direct access to your filesystem and allows them to run background processes that phone home.

**The pragmatic approach:** Run Tier 1 for your family's life. Run Tier 2 for the things your boss or your kid's school forces you to use. That alone is a massive win.

---

## Layer 6: Endpoint Hardening — The Family Devices

### Operating System

We run **LemonKaijuOS** — a custom image built on top of [Bazzite](https://bazzite.gg/), which is itself built on Fedora Silverblue. This gives us:
- An **immutable, atomic OS** — the core operating system cannot be modified by malware or kids
- **Gaming-optimised** (important in our house)
- Custom configurations pre-baked in, deployed from a Git repository

For families who just want hardened Linux without the gaming focus, **Fedora Workstation** or **Linux Mint** are solid, beginner-friendly choices.

### Browsers

| Browser | Best for | Why |
|---|---|---|
| **Brave** | Daily use | Blocks ads by default, randomises browser fingerprint, doesn't break websites |
| **LibreWolf** | Privacy-first use | Hardened Firefox fork, all Mozilla telemetry removed, strict defaults |
| **Firefox** (hardened) | Intermediate users | Extensible, pair with uBlock Origin + arkenfox `user.js` |

**Avoid:** Chrome (Google surveillance), Edge (Microsoft surveillance), Safari on Windows.

### Parental Controls — Local, not cloud

The key principle: **parental controls shouldn't report your kids' behaviour to a third party.**

Our approach:
1. **No admin accounts for kids.** Kids' accounts don't have `sudo` access — they cannot install software, change DNS settings, or bypass system rules.
2. **Timekpr-nExT** — local screen time management. Sets daily limits, schedules, and can lock or terminate sessions. All data stays on your machine.

---

## What this doesn't protect against

We want to be honest about limitations. This setup does **not** protect against:

- **Compromised devices.** If malware gets on an endpoint before your controls are in place, it can exfiltrate data through legitimate channels.
- **Mobile data.** When your kids use mobile data instead of home Wi-Fi, they bypass your entire stack. Mobile DNS and VPN configurations on phones are a separate layer.
- **Social engineering.** No firewall stops a kid giving their password to someone online.
- **Endpoint-level surveillance apps.** If a device ships with preinstalled spyware (some budget Android phones do), that's a hardware/trust problem.
- **Determined technically skilled users.** A tech-savvy teenager can find workarounds. This is about raising the floor for casual threats, not building an unbreachable fortress.

---

## Where to start if you're overwhelmed

Do these **in order** — each one is useful on its own:

1. **Just change your DNS** — Point your home router's DNS to a free privacy-respecting resolver like `1.1.1.1` (Cloudflare) or `9.9.9.9` (Quad9). Not as powerful as AdGuard, but immediate improvement with zero setup.
2. **Install AdGuard Home** on a Raspberry Pi or any spare computer.
3. **Switch browsers** — Brave on every family device. Free, takes 5 minutes.
4. **Get a VPS and set up WireGuard** — Stage 2 of this guide will make this point-and-click.
5. **Deploy OPNsense** when you're ready for the deep end.

---

## What's coming in Stage 2

Stage 2 of this project is a **Guided Deployment Application**. 

The stack in this guide is effective but requires significant technical knowledge to deploy. The Stage 2 installer makes deployment feel like installing an app, not configuring a server. 

It runs locally in your browser, conducts an interview about your home network, and features a local AI assistant that helps you configure the VPS, OPNsense, the Homelab, and the endpoints without you ever having to look at a terminal wall of text.

---

## Contributing & keeping this guide alive

This guide is built from a real family's real network. As we deploy each layer, we update our internal setup tracker, and the guide reflects our actual experience — not theoretical recommendations.

If you try any of this and find something that didn't work as described, we want to know. This is a living document.

---

*Guide version: 0.1 (Stage 1 — Planning & Concepts)*
*Last updated: 2026-03-11*
*Derived from: `network_setup_tracker.md`*
