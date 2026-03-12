# Shut The Front Door! - Installer

**Stage 2: Guided Deployment Application**

A browser-based installer that helps non-technical parents deploy a state-of-the-art privacy-preserving home network without requiring terminal access or Linux knowledge.

## Quick Start

### For Users

1. **Download the installer** (`setup.exe` for Windows, or run `python start.py` for other platforms)
2. **Run the installer** - it will open automatically in your browser
3. **Follow the guided interview** to configure your network
4. **Deploy services** with one-click installation
5. **Configure devices** using the provided guides

### For Developers

```bash
# Clone the repository
git clone https://github.com/your-org/shut-the-front-door.git
cd shut-the-front-door/installer

# Install dependencies
pip install -r requirements.txt

# Run the installer
python start.py
```

The installer will start a local web server and open your browser automatically.

## Features

### 🎯 User-Friendly
- **Browser-based interface** - no terminal required
- **Guided interview** - plain English questions
- **Progress tracking** - see exactly what's happening
- **Error handling** - human-readable explanations

### 🤖 AI Assistant
- **Hardware detection** - automatically configures based on your computer
- **Local AI** - runs entirely on your machine (no cloud dependencies)
- **Fallback mode** - works even without AI capabilities
- **Plain English help** - explains technical concepts simply

### 🔧 Modular Deployment
- **WireGuard VPN** - hide your home IP address
- **AdGuard Home** - block ads and trackers network-wide
- **OPNsense** - professional firewall configuration
- **Authentik** - centralized family login system
- **Nextcloud** - private cloud storage
- **Device hardening** - privacy-focused endpoint setup

### 🛡️ Privacy First
- **Local only** - no data sent to external services
- **Zero cloud dependencies** - everything runs on your hardware
- **Open source** - all code is auditable
- **Family focused** - designed for non-technical users

## Architecture

### Installation Flow

```
Welcome Screen → Setup Interview → Deployment → Completion
     ↓                ↓              ↓           ↓
  Introduction    Network Config   Service     Device
  & Features      Collection      Setup      Guides
```

### Hardware Tiers

The installer automatically detects your hardware and configures the AI accordingly:

| Tier | Requirements | AI Model | Features |
|------|-------------|----------|----------|
| **GPU** | Dedicated GPU + 16GB+ RAM | Llama 3.1 8B | Full AI assistant |
| **CPU** | 16GB+ RAM, no GPU | Phi-3 Mini 3.8B | AI assistant (smaller) |
| **Fallback** | Any hardware | Scripted responses | Guided wizard |

### Module Structure

```
installer/
├── start.py              ← Entry point
├── server.py             ← Flask web server
├── requirements.txt      ← Python dependencies
├── modules/              ← Deployment modules
│   ├── wireguard.py     ← WireGuard VPN
│   ├── opnsense.py      ← OPNsense firewall
│   ├── adguard.py       ← AdGuard Home DNS
│   ├── authentik.py     ← Authentik SSO
│   ├── nextcloud.py     ← Nextcloud cloud
│   └── endpoints.py     ← Device configuration
├── ai/                   ← AI integration
│   ├── assistant.py     ← AI logic
│   └── __init__.py
├── web/                  ← Browser interface
│   ├── index.html       ← Main UI
│   ├── style.css        ← Dark theme styling
│   └── app.js           ← Frontend logic
└── templates/            ← Configuration templates
```

## Configuration Files

The installer creates several important files:

- `install_config.json` - Your interview answers and preferences
- `install_log.json` - Timestamped record of all installation actions
- `network_setup_tracker.md` - Updated after each successful module
- `generated_configs/` - Service-specific configuration files

## Development

### Adding New Modules

1. Create a new module file in `modules/`
2. Implement the `deploy_[module_name](config)` function
3. Add the module to `modules/__init__.py`
4. Update the server's module list in `server.py`
5. Add UI elements in `web/index.html`

### AI Integration

The AI assistant supports three modes:

1. **Full LLM** - Uses Ollama with local models
2. **Scripted** - Pattern-based responses
3. **Fallback** - Basic help messages

To modify AI behavior:
- Edit `ai/assistant.py`
- Update the `SYSTEM_PROMPT`
- Add new response patterns in `get_scripted_response()`

### Testing

```bash
# Test individual modules
python -m modules.wireguard
python -m modules.adguard

# Test AI assistant
python -m ai.assistant

# Run with development server
python server.py
```

## Security Considerations

- **No external connections** - Everything runs locally
- **No data collection** - No telemetry or analytics
- **Config encryption** - Sensitive data is protected
- **Audit logging** - All actions are recorded
- **Open source** - Code can be independently audited

## Troubleshooting

### Common Issues

**Port already in use:**
- The installer automatically finds available ports
- Check if other services are using ports 3000-3010

**SSH connection failures:**
- Verify VPS/homelab IP addresses are correct
- Check SSH key paths and permissions
- Ensure target machines are accessible

**Docker installation failures:**
- Verify target OS supports Docker
- Check internet connectivity on target machines
- Review Docker installation logs

**AI assistant not working:**
- Install Ollama from https://ollama.com/
- Download required models: `ollama pull llama3.1:8b`
- Check hardware requirements for local AI

### Getting Help

1. Check the installation logs in `install_log.json`
2. Review the network setup tracker
3. Consult the main project documentation
4. Open an issue on GitHub with details about your setup

## Contributing

We welcome contributions! Areas where help is needed:

- **Additional hardware support** - GPU detection for more vendors
- **More deployment modules** - Additional privacy services
- **UI improvements** - Better accessibility and usability
- **Documentation** - Translation and clearer explanations
- **Testing** - More comprehensive test coverage

## License

MIT License - see LICENSE file for details.

## Support

This is a community project. For support:

1. Check the documentation and troubleshooting guides
2. Search existing GitHub issues
3. Create a new issue with detailed information
4. Join community discussions (links in main project)

---

**Remember:** This installer is designed to make enterprise-grade privacy accessible to everyone. No technical knowledge required!
