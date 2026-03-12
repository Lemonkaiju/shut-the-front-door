# Project Handoff: Shut The Front Door!

Welcome to the **Shut The Front Door!** codebase. This document is written to give incoming AI agents (like Windsurf) immediate working context on what this project is, what the goals are, and how the codebase works.

## 1. Project Overview

**Goal:** Provide a non-technical pathway for parents to build a state-of-the-art privacy-preserving home network. We want to stop corporate telemetry, age-verification scraping, and advertising tracking at the edge of the network, without forcing parents to learn Linux command-line administration. 

**Wait, what?**
Most privacy guides are written for sysadmins: *"Just install pfsense, configure an unbound resolver, and self-host nextcloud."* Regular parents hit that wall and give up. This project lowers the skill floor to "can follow a wizard."

**Core Principles:**
1. **Local first:** The setup uses zero cloud dependencies. No SaaS, no subscriptions. You own the hardware, you own the data.
2. **Plain English:** All UI and documentation must adhere to the `plain_language_guide.md`. Technical terms are banned from the primary UI. "DNS Sinkhole" becomes "The Filter". 
3. **No Terminal Required:** The end-user should *never* have to open a terminal to deploy this stack.

## 2. The Stack

The privacy architecture is tiered into six layers:

1. **The Front Door:** WireGuard VPN running on a cheap cloud VPS (masks home IP).
2. **The Gatekeeper:** OPNsense running on a local mini-PC firewall (controls network flow).
3. **The Filter:** AdGuard Home running via Docker on a homelab server (DNS blocklist and parental controls).
4. **Sovereign Identity:** Authentik SSO running via Docker (centralized family logins).
5. **Private Cloud:** Nextcloud running via Docker (replaces Google Drive/Photos).
6. **Endpoints:** Linux machines using Bazzite or Linux Mint, hardened browsers (Brave), and local screen time tools (Timekpr-nExT). 

## 3. Project Stages

**Stage 1: The Guide (Done)**
The `guide/digital_resistance_guide.md` is the "what" and "why" handbook explaining the stack. It lives in this repo and will be published via GitHub Pages.

**Stage 2: The Installer (Current Focus)**
This is the core software product. The specifications are in `installer/spec.md`. The installer is a **local Python web server** packaged as a `.exe`. When a user runs it, it opens a wizard in their browser. It interviews them about their network, and then uses a local Ollama AI model to intelligently run the Ansible/Bash/SSH scripts in the background to set up the stack on their various servers.

**Stage 3: Mission Control (Future)**
An ongoing, local RAG-enabled chatbot that the parent can use to manage their network after it is installed.

## 4. Where we are right now

We have completed the conceptual design and the Stage 1 documentation. We are currently preparing to build the **Stage 2 Installer**, starting with deployment module 1 (WireGuard on VPS).

## 5. Important Note on Windows + GitHub MCP Server

This project uses the GitHub Model Context Protocol (MCP) server heavily to manage version control directly through the agent. 

**CRITICAL FIX ALREADY APPLIED:** By default, the `github` MCP server configuration tries to use Docker to run. The user's Windows machine does *not* have Docker Desktop installed in the Windows environment, which previously caused an `exec: "docker": executable file not found in %PATH%` error. 

To fix this, the `mcp_config.json` was rewritten to use `npx` with Node.js instead, like this:

```json
"github": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-github"
  ],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "<redacted>"
  }
}
```

**If you need to restart or reconfigure the MCP server, you MUST use the `npx` configuration above. Do not revert it to Docker.** Node.js is installed natively on the host.

## 6. Key Files to Read First

- `README.md` — The public-facing entry point.
- `installer/spec.md` — The architectural blueprint for what you are about to build.
- `plain_language_guide.md` — The rules for writing any UI copy or user-facing text.
- `network_setup_tracker.md` — The living document tracking the actual state of the testbed network as modules are built.
