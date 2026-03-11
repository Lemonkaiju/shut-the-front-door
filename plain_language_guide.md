# Plain Language Guide
### How we talk to parents — not sysadmins

> This document is the voice and terminology reference for all user-facing text in the installer UI, the guide, and any error messages. If a word appears in the left column, use the right column instead everywhere the parent will read it.

---

## Tier Names (what we call the setup levels)

| Technical name | What we call it |
|---|---|
| Tier 1 — DNS Sinkhole | 🛡️ **The Filter** — *"Stop the junk before it reaches your kids"* |
| Tier 2 — VPN Front Door | 🚪 **The Front Door** — *"Control what the outside world sees about your home"* |
| Tier 3 — Edge Firewall | 🔒 **The Gatekeeper** — *"Full control over every device on your network"* |
| Tier 4 — Private Cloud | 🏠 **Your Family's Private Space** — *"Your photos, files, and accounts — on your terms"* |

---

## Technology → Plain English

| Tech term | Say this instead |
|---|---|
| VPS (Virtual Private Server) | A small computer we rent in another country to act as your home's private mailbox |
| WireGuard / VPN | A private tunnel your internet traffic travels through |
| DNS | The phone book your devices use to find websites |
| DNS Sinkhole | A filter that tears out the bad pages before your devices can look them up |
| AdGuard Home | Your family's ad and tracker blocker |
| OPNsense | The gatekeeper box that controls everything going in and out of your home network |
| Firewall | A security guard for your network |
| Docker / Container | A self-contained app that runs without affecting the rest of the computer |
| SSH | A secure remote connection to another computer |
| SSH Key | A password that's too long and complex to guess — generated automatically |
| Authentik | Your family's private login system — like "Sign in with Google" but yours |
| SSO (Single Sign-On) | One password to log into everything |
| Nextcloud | Your family's private Google Drive |
| VLAN | A separate "room" on your network for different devices |
| Subnet | The address range your home network uses |
| Port 53 | The door that DNS requests go through |
| Flatpak | A safe way to install apps on Linux |
| Immutable OS | An operating system that can't be accidentally broken |
| Telemetry | Data your device secretly sends back to the company that made it |
| Endpoint | Any device on your network (laptop, phone, tablet, console) |
| NIC | A network port on a computer |

---

## Warning Messages — Plain English Rewrites

### DNS enforcement without a firewall
❌ *"Without OPNsense NAT rules, port 53 hijacking cannot be enforced."*

✅ *"Without the Gatekeeper box, some stubborn devices (like smart TVs) can ignore your filter and look up anything they want. It's still worth having the filter — most devices will respect it. You can add the Gatekeeper later if you want the full lockdown."*

---

### SSH connection failed
❌ *"Error: ECONNREFUSED — connection to host timed out"*

✅ *"We couldn't connect to your desired computer. Double-check the IP address you entered, and make sure SSH access is turned on. [How to do this →]"*

---

### Docker pull in progress
❌ *(silent, or scrolling output)*

✅ *"Downloading The Filter software... this usually takes 1–3 minutes depending on your connection."*

---

### Child account creation
❌ *"Creating non-privileged user account and excluding from sudoers group"*

✅ *"Setting up [child's name]'s account so they can't accidentally (or intentionally) change system settings."*

---

### Tier skipped warning
❌ *"Module 2 (OPNsense) not selected. DNS enforcement will not be applied at the network level."*

✅ *"You've skipped the Gatekeeper for now — that's totally fine. Just know that your filter works for most devices but won't be able to catch the stubborn ones. You can add the Gatekeeper any time later."*

---

## Installer UI Copy — Voice Guide

**Tone:** Calm, capable, like a knowledgeable friend helping you move house. Not corporate. Not condescending. Not panicked.

**Rules:**
- Never use an acronym without first explaining it in plain English — and then use the plain English version from then on
- Always explain *why* before *what* — "We're going to set up your filter first because it protects every device immediately"
- Progress bars should have human descriptions, not technical ones: *"Setting up your filter (2 of 4 steps)"* not *"Pulling adguard/adguardhome:latest"`*
- Errors should always end with a next step — never a dead end
- Success messages should feel like a small win: *"Done! Your family's filter is running ✅"*

---

## Onboarding — First Screen Copy (Draft)

> ### Welcome.
>
> You've decided to take back control of your family's internet. That's a big deal.
>
> This tool will walk you through setting up your own private, secure home network — one step at a time. You don't need to be technical. Every step will explain what's happening and why before anything changes.
>
> **How long will this take?**
> Depends on what you want to set up. The first layer takes about 20 minutes. The full setup takes a few hours across a weekend.
>
> **What will you need?**
> We'll ask you what you have before we start. You don't need everything — you can begin with almost nothing and add more later.
>
> Ready? Let's find out where you're starting from. →

---

## Error Hierarchy (how serious to make things sound)

| Situation | Tone |
|---|---|
| Step succeeded | Warm, brief confirmation — don't over-celebrate |
| Step took longer than expected | Reassuring — "still working, this can take a minute" |
| Step failed but is retryable | Calm, clear cause, single next action |
| Step failed, needs user input | Clear ask, no jargon, link to help if relevant |
| Critical failure (can't proceed) | Honest, no panic, explicit options (retry / skip / get help) |

Never: technical error codes in the primary message. Always: one obvious next step.
