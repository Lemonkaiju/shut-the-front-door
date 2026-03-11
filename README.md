# 🚪 Shut The Front Door!

**Take back control of your family's internet. No tech degree required.**

Shut The Front Door is a guided toolkit for parents and privacy-conscious households who want to stop being tracked, protect their kids, and own their data — without handing control to a corporation.

> **Why trust this?** We don't sell anything, there are no subscriptions, and we don't have a cloud. Everything runs 100% locally on your own hardware, and every piece of software we recommend is public, open-source, and auditable. Built by parents, for parents.

---

## What this is

A two-part project:

**Stage 1 — The Guide**
A plain-English handbook explaining what you're protecting against, what tools we use, and why. Written by a parent, for parents.
→ [Read the guide](guide/digital_resistance_guide.md)

**Stage 2 — The Installer** *(coming soon)*
A local web app that walks you through deploying the entire stack, one step at a time. No terminal required. Includes an AI assistant that troubleshoots errors in plain English.

---

## The stack

| What we call it | What it does | Tech underneath |
|---|---|---|
| 🛡️ The Filter | Blocks ads and trackers for every device | AdGuard Home |
| 🚪 The Front Door | Hides your home IP, bypasses age gates | WireGuard VPN on a VPS |
| 🔒 The Gatekeeper | Full control over your network traffic | OPNsense |
| 🏠 Your Family's Private Space | Replace Google Drive, Photos, accounts | Authentik + Nextcloud |

---

## Start here

**You don't need everything.** Pick the level that matches what you have:

- 🟢 **Just a spare computer or Raspberry Pi?** → Start with [The Filter](guide/digital_resistance_guide.md#layer-3-dns-sinkhole--adguard-home)
- 🟡 **Have a spare computer + willing to pay ~$5/month?** → Add [The Front Door](guide/digital_resistance_guide.md#layer-1-the-front-door--your-vps--vpn)
- 🔵 **Want the full setup?** → [Read the full guide](guide/digital_resistance_guide.md)

---

## What this protects against

- ISP surveillance and data selling
- Corporate ad tracking across every website
- Regional age-verification blocks
- Smart devices phoning home
- Kids bypassing parental controls via cloud

[Full threat model →](guide/digital_resistance_guide.md#the-threat-model--what-are-we-actually-defending-against)

---

## What's coming

The Stage 2 installer will provide:
- A local web app (opens in your browser — no terminal needed)
- An AI assistant running entirely on your machine that troubleshoots in plain English
- One-command deployment for every layer
- Works from Windows, Mac, or Linux

---

## Contributing

This guide is built from a real family's real network. If you try something and it doesn't work as described, open an issue. Every problem you hit makes the guide better for the next parent.

---

## License

[MIT](LICENSE) — free to use, share, and adapt.

*Last updated: 2026-03-11*
