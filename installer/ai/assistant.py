"""
Shut The Front Door! - AI Assistant
Stage 2: Guided Deployment Application

AI assistant that helps users through the installation process.
Supports multiple hardware tiers with fallback to scripted responses.
"""

import json
import psutil
import platform
from pathlib import Path
from typing import Dict, Any, Optional

PROVISIONING_STATE = {
    'status': 'idle', # idle, running, success, error
    'step': '', # checking_ollama, installing_ollama, checking_model, downloading_model, ready
    'message': '',
    'progress': 0,
    'error': None
}

def get_provisioning_status():
    return PROVISIONING_STATE

def start_provisioning(config=None):
    if PROVISIONING_STATE['status'] == 'running':
        return
    PROVISIONING_STATE['status'] = 'running'
    PROVISIONING_STATE['error'] = None
    
    import threading
    thread = threading.Thread(target=_provision_thread, daemon=True)
    thread.start()

def _provision_thread():
    import time
    try:
        PROVISIONING_STATE['step'] = 'checking_ollama'
        PROVISIONING_STATE['message'] = 'Checking AI engine availability...'
        PROVISIONING_STATE['progress'] = 10
        
        hardware = detect_hardware_tier()
        if hardware['tier'] == 'fallback':
            PROVISIONING_STATE['status'] = 'success'
            PROVISIONING_STATE['step'] = 'ready'
            PROVISIONING_STATE['message'] = 'Using scripted responses (no AI needed)'
            PROVISIONING_STATE['progress'] = 100
            return

        # Check Ollama
        if not check_ollama_availability():
            PROVISIONING_STATE['step'] = 'installing_ollama'
            PROVISIONING_STATE['message'] = 'Installing AI engine...'
            install_success = install_ollama_if_needed()
            if not install_success:
                raise Exception("Failed to install AI engine")
                
        # Give Ollama a second to start
        time.sleep(2)
            
        PROVISIONING_STATE['step'] = 'checking_model'
        PROVISIONING_STATE['message'] = 'Checking AI models...'
        PROVISIONING_STATE['progress'] = 50
        
        # Determine model
        model_name = 'llama3.1:8b' if hardware['tier'] == 'gpu' else 'phi3:mini'
        
        # Check and download model
        download_model_with_progress(model_name)
        
        PROVISIONING_STATE['status'] = 'success'
        PROVISIONING_STATE['step'] = 'ready'
        PROVISIONING_STATE['message'] = 'AI Assistant is ready'
        PROVISIONING_STATE['progress'] = 100
        
    except Exception as e:
        PROVISIONING_STATE['status'] = 'error'
        PROVISIONING_STATE['error'] = str(e)
        PROVISIONING_STATE['message'] = 'Provisioning failed'

# Context for the AI assistant
SYSTEM_PROMPT = """
You are a helpful AI assistant for the "Shut The Front Door!" privacy network installer.
Your role is to guide non-technical parents through setting up a privacy-preserving home network.

Key principles:
1. Use plain English - avoid technical jargon
2. Be patient and encouraging
3. Explain concepts simply
4. Never assume technical knowledge
5. Focus on privacy and family safety
6. Provide step-by-step guidance
7. Offer alternatives when things go wrong

The installer helps deploy:
- The Front Door: WireGuard VPN on cloud VPS
- The Filter: AdGuard Home DNS blocking
- The Gatekeeper: OPNsense firewall (with Local Breakout for streaming)
- Family Identity: Authentik SSO
- Private Cloud: Nextcloud
- Device Setup: Privacy-focused endpoints

Always prioritize user privacy and security. If you don't know something, admit it and suggest checking the documentation.
"""

def detect_hardware_tier() -> Dict[str, Any]:
    """
    Detect hardware capabilities and determine AI tier.
    
    Returns:
        Dict with hardware tier and capabilities
    """
    try:
        # Get system information
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Check for GPU
        gpu_info = detect_gpu()
        
        # Determine tier
        if gpu_info and memory_gb >= 16:
            tier = 'gpu'
            model = 'Llama 3.1 8B'
            description = 'Full AI assistant with local LLM'
        elif memory_gb >= 16:
            tier = 'cpu_capable'
            model = 'Phi-3 Mini 3.8B'
            description = 'AI assistant with smaller local LLM'
        else:
            tier = 'fallback'
            model = 'Scripted responses'
            description = 'Guided wizard without AI'
        
        return {
            'tier': tier,
            'model': model,
            'description': description,
            'cpu_count': cpu_count,
            'memory_gb': round(memory_gb, 1),
            'gpu_info': gpu_info,
            'platform': platform.system()
        }
        
    except Exception as e:
        return {
            'tier': 'fallback',
            'model': 'Scripted responses',
            'description': 'Error detecting hardware, using fallback',
            'error': str(e)
        }

def detect_gpu() -> Optional[Dict[str, Any]]:
    """Detect GPU information."""
    try:
        # Try to detect NVIDIA GPU
        try:
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            
            if device_count > 0:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                return {
                    'type': 'nvidia',
                    'name': name,
                    'memory_mb': memory.total // (1024**2),
                    'device_count': device_count
                }
        except ImportError:
            pass
        except Exception:
            pass
        
        # Try to detect AMD GPU
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return {
                    'type': 'amd' if 'AMD' in gpu.name else 'other',
                    'name': gpu.name,
                    'memory_mb': gpu.memoryTotal,
                    'device_count': len(gpus)
                }
        except ImportError:
            pass
        except Exception:
            pass
        
        return None
        
    except Exception:
        return None

def get_ai_response(message: str, config: Dict[str, Any]) -> str:
    """
    Get AI response based on hardware tier and message.
    
    Args:
        message: User message
        config: Installation configuration
        
    Returns:
        AI response string
    """
    hardware = detect_hardware_tier()
    
    if hardware['tier'] == 'gpu':
        return get_llm_response(message, config, hardware)
    elif hardware['tier'] == 'cpu_capable':
        return get_llm_response(message, config, hardware)
    else:
        return get_scripted_response(message, config, hardware)

def get_llm_response(message: str, config: Dict[str, Any], hardware: Dict[str, Any]) -> str:
    """
    Get response from local LLM (Ollama).
    
    Args:
        message: User message
        config: Installation configuration
        hardware: Hardware information
        
    Returns:
        LLM response string
    """
    try:
        import requests
        
        # Get context from installation state
        context = get_installation_context(config)
        
        # Build prompt
        prompt = f"""
{SYSTEM_PROMPT}

Current Installation Context:
{context}

User Question: {message}

Please provide a helpful, plain English response that guides the user through their privacy network setup.
"""
        
        # Call Ollama API
        model_name = 'llama3.1:8b' if hardware['tier'] == 'gpu' else 'phi3:mini'
        
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': model_name,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.7,
                'max_tokens': 500
            }
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'I had trouble understanding that. Could you rephrase your question?')
        else:
            return get_scripted_response(message, config, hardware)
            
    except Exception as e:
        print(f"LLM error: {e}")
        return get_scripted_response(message, config, hardware)

def get_scripted_response(message: str, config: Dict[str, Any], hardware: Dict[str, Any]) -> str:
    """
    Get scripted response based on message content and installation state.
    
    Args:
        message: User message
        config: Installation configuration
        hardware: Hardware information
        
    Returns:
        Scripted response string
    """
    
    # Convert message to lowercase for matching
    message_lower = message.lower()
    
    # Installation stage detection
    current_stage = detect_installation_stage(config)
    
    # Common responses based on keywords
    responses = {
        # Greetings and general help
        ('hello', 'hi', 'help', 'start'): [
            "Hello! I'm here to help you set up your privacy network. What would you like to know about?",
            "Hi there! I can guide you through setting up your family's privacy network. What's on your mind?",
            "Welcome! I'm your privacy network assistant. How can I help you today?"
        ],
        
        # WireGuard questions
        ('vpn', 'wireguard', 'front door', 'vps'): [
            "The Front Door (WireGuard VPN) hides your home IP address from websites and services. It's like having a secure tunnel for all your internet traffic.",
            "WireGuard creates a private connection between your home and a cloud server. This helps protect your privacy and bypass regional restrictions.",
            "The VPN setup requires a cloud server (VPS) that costs about $5/month. I can help you choose a provider and set it up."
        ],
        
        # DNS filtering questions
        ('dns', 'adguard', 'filter', 'ads', 'tracking'): [
            "The Filter (AdGuard Home) blocks ads and trackers on every device in your home. It's like having an ad-blocker for your entire network.",
            "AdGuard Home works at the DNS level to prevent ads and trackers from loading. This makes websites load faster and protects your privacy.",
            "DNS filtering stops tracking cookies, ads, and malicious websites before they reach your devices. It's much more effective than browser ad-blockers."
        ],
        
        # Firewall questions
        ('firewall', 'opnsense', 'gatekeeper', 'security'): [
            "The Gatekeeper (OPNsense) is a professional-grade firewall that controls what internet traffic enters and leaves your home network.",
            "OPNsense gives you complete control over your network. You can block unwanted connections and monitor all traffic.",
            "A firewall is like a security guard for your internet connection. It checks all traffic and only allows what you approve."
        ],
        
        # Authentication questions
        ('login', 'accounts', 'authentik', 'identity'): [
            "Family Identity (Authentik) creates secure login accounts for everyone in your family. No more remembering dozens of passwords!",
            "Authentik provides one login for all your family services. Parents get admin access, and children get appropriate restrictions.",
            "Single sign-on means you login once and get access to all your family services. It's secure and convenient."
        ],
        
        # Cloud storage questions
        ('nextcloud', 'cloud', 'storage', 'photos', 'files'): [
            "Private Cloud (Nextcloud) replaces Google Drive and Dropbox with your own secure storage. Your files stay in your home.",
            "Nextcloud gives you file sharing, photo albums, calendars, and contacts - all hosted on your own hardware. No corporation has access to your data.",
            "With Nextcloud, you can store photos, documents, and share files with family members. It's like having your own private Google services."
        ],
        
        # Device setup questions
        ('devices', 'computers', 'phones', 'endpoints'): [
            "Device setup involves installing privacy-focused software on all your family computers and phones. I recommend Bazzite Linux for computers.",
            "For computers, I suggest Bazzite Linux - it's secure, private, and family-friendly. For phones, we'll configure privacy settings and VPN connections.",
            "Each device needs proper DNS settings, VPN connection, and privacy-focused browsers. I'll guide you through each device type."
        ],
        
        # Technical troubleshooting
        ('error', 'problem', 'issue', 'trouble', 'not working'): [
            "I'm sorry you're having trouble! Let me help you troubleshoot. Can you tell me which step you're on and what error you're seeing?",
            "Don't worry - technical issues happen to everyone. Please describe what you're trying to do and what's going wrong, and I'll help you fix it.",
            "Let's solve this together. What service are you setting up, and what specific problem are you encountering?"
        ],
        
        # Cost questions
        ('cost', 'price', 'money', 'free', 'expensive'): [
            "Most of the privacy network is free! The only ongoing cost is the VPS for WireGuard (about $5/month). Everything else runs on your own hardware.",
            "The privacy stack is designed to be affordable. You'll need a cloud server (~$5/month) and optionally a homelab server (can use an old computer).",
            "Unlike commercial services, there are no subscriptions or data fees. You own your hardware and your data forever."
        ],
        
        # Privacy questions
        ('privacy', 'secure', 'safe', 'protect'): [
            "This setup protects your family from corporate tracking, data collection, and surveillance. Everything runs locally on your own hardware.",
            "Your privacy is protected through multiple layers: VPN hides your IP, DNS filtering blocks trackers, and local storage keeps data out of corporate hands.",
            "The privacy network stops ISPs from selling your data, prevents ad tracking, and gives you control over your family's digital footprint."
        ],
        
        # Streaming & Geoblocking questions
        ('streaming', 'netflix', 'amazon', 'disney', 'geoblock', 'australia', 'breakout'): [
            "The Regional Access Optimization ensures local Australian streaming services (like ABC, SBS, Stan) always work by routing them through your local internet instead of the VPN.",
            "If you want to watch international Netflix or Amazon libraries, keep the 'Global Streaming Breakout' option OFF. If you prefer the local library, turn it ON.",
            "Streaming services often block VPNs. Our 'Local Breakout' feature automatically routes streaming traffic outside the VPN so you don't get blocked."
        ],
        
        # Browser & Fingerprinting questions
        ('browser', 'mullvad', 'fingerprinting', 'tracking', 'privacy'): [
            "Mullvad Browser is the best choice for families because it has anti-fingerprinting built-in. It makes every user look identical to websites, preventing tracking without cookies.",
            "Browser fingerprinting is how sites track you even without cookies. Mullvad Browser hides your screen resolution, fonts, and hardware details by default.",
            "Unlike regular browsers, Mullvad Browser uses 'letterboxing' - grey bars around websites - so sites can't see your actual monitor size. It's perfect for kids and non-technical users."
        ],
        
        # Device setup questions
        ('lemonkaiju', 'device', 'computer', 'setup'): [
            "LemonKaijuOS includes Mullvad Browser by default for maximum privacy. Just install it and launch - no configuration needed.",
            "For device setup, I recommend Mullvad Browser for everyday use and LibreWolf for advanced users who want more control.",
            "The key is using browsers that prevent fingerprinting. Even with a VPN, sites can still track you through your browser's unique characteristics unless you use Mullvad Browser."
        ]
    }
    
    # Find matching response
    for keywords, response_list in responses.items():
        if any(keyword in message_lower for keyword in keywords):
            import random
            return random.choice(response_list)
    
    # Context-aware responses based on installation stage
    stage_responses = {
        'welcome': [
            "Ready to start your privacy journey? I'll guide you through each step. Let's begin with the setup interview to understand your needs.",
            "Great! Let's get your family's privacy network set up. First, I need to know about your current network and what services you'd like to deploy."
        ],
        'interview': [
            "I'm here to help with the setup interview. Please provide your network details like your VPS information and home network configuration.",
            "Let's gather the information needed for your privacy network. Don't worry if you're not sure about some details - I'll help you figure them out."
        ],
        'deployment': [
            "Deployment is starting! Each service will be installed automatically. If anything fails, I'll help you troubleshoot and fix it.",
            "Your privacy network is being deployed now. This may take 15-30 minutes. I'll monitor the progress and help with any issues that come up."
        ],
        'completion': [
            "Congratulations! Your privacy network is set up. Next, we'll configure your devices to use the new DNS settings and VPN connections.",
            "Great work! Your family's privacy network is running. Let me help you configure your devices and get the most out of your new setup."
        ]
    }
    
    if current_stage in stage_responses:
        import random
        return random.choice(stage_responses[current_stage])
    
    # Default responses
    default_responses = [
        "That's a great question! Based on your current setup, I'd recommend checking the installation guide or asking me about a specific service.",
        "I'm here to help! Could you tell me more about what you'd like to know? I can explain any part of the privacy network setup.",
        "Good question! Let me help you with that. Are you asking about the VPN, DNS filtering, cloud storage, or something else?",
        "I'd be happy to help! Can you provide more details about what you're trying to accomplish with your privacy network?"
    ]
    
    import random
    return random.choice(default_responses)

def get_installation_context(config: Dict[str, Any]) -> str:
    """Get current installation context for AI."""
    
    context_parts = []
    
    # Installation stage
    stage = detect_installation_stage(config)
    context_parts.append(f"Current Stage: {stage}")
    
    # Configuration status
    if config:
        if config.get('vps_ip'):
            context_parts.append(f"VPS configured: {config['vps_ip']}")
        if config.get('homelab_ip'):
            context_parts.append(f"Homelab server: {config['homelab_ip']}")
        if config.get('family_size'):
            context_parts.append(f"Family size: {config['family_size']} members")
        if config.get('services'):
            context_parts.append(f"Selected services: {', '.join(config['services'])}")
        if config.get('bypass_global') is not None:
            status = 'ON' if config.get('bypass_global') else 'OFF'
            context_parts.append(f"Global Streaming Breakout: {status}")
    else:
        context_parts.append("No configuration saved yet")
    
    return '\n'.join(context_parts)

def detect_installation_stage(config: Dict[str, Any]) -> str:
    """Detect current installation stage based on configuration."""
    
    if not config or not any(config.values()):
        return 'welcome'
    
    if config.get('vps_ip') or config.get('homelab_ip'):
        if config.get('services'):
            return 'deployment'
        else:
            return 'interview'
    
    return 'interview'

def check_ollama_availability() -> bool:
    """Check if Ollama is available and running."""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def install_ollama_if_needed() -> bool:
    """
    Install Ollama if it's not available.
    
    Returns:
        True if installation was successful or already available
    """
    if check_ollama_availability():
        return True
    
    try:
        import subprocess
        import platform
        import os
        import urllib.request
        import tempfile
        import time
        
        system = platform.system().lower()
        
        if system == 'windows':
            PROVISIONING_STATE['message'] = 'Downloading AI engine for Windows...'
            exe_path = os.path.join(tempfile.gettempdir(), 'OllamaSetup.exe')
            urllib.request.urlretrieve('https://ollama.com/download/OllamaSetup.exe', exe_path)
            
            PROVISIONING_STATE['message'] = 'Installing AI engine silently...'
            subprocess.run([exe_path, '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART'], check=True)
            
            for _ in range(15):
                if check_ollama_availability():
                    return True
                time.sleep(2)
            return False
            
        elif system == 'linux':
            PROVISIONING_STATE['message'] = 'Installing AI engine for Linux...'
            subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh', '|', 'sh'], check=True, shell=True)
            return check_ollama_availability()
        else:
            print("Ollama installation not supported on this platform")
            return False
            
    except Exception as e:
        print(f"Failed to install Ollama: {e}")
        return False

def download_model_with_progress(model_name: str) -> bool:
    """
    Download required model with progress tracking.
    """
    try:
        import requests
        import json
        
        # Check if model is available
        response = requests.post('http://localhost:11434/api/show', json={'name': model_name}, timeout=10)
        if response.status_code == 200:
            return True
        
        PROVISIONING_STATE['step'] = 'downloading_model'
        PROVISIONING_STATE['message'] = f'Downloading {model_name} (this may take a while)...'
        
        # Download model
        print(f"Downloading {model_name} model...")
        response = requests.post('http://localhost:11434/api/pull', json={
            'name': model_name,
            'stream': True
        }, stream=True, timeout=300)
        
        if response.status_code != 200:
            raise Exception(f"Failed to start model download: {response.status_code}")
            
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if 'total' in data and 'completed' in data and data['total'] > 0:
                    percent = int((data['completed'] / data['total']) * 100)
                    PROVISIONING_STATE['progress'] = 50 + int(percent * 0.45)
                    PROVISIONING_STATE['message'] = f"Downloading {model_name} ({percent}%)..."
        
        return True
        
    except Exception as e:
        print(f"Failed to download model {model_name}: {e}")
        raise

if __name__ == '__main__':
    # Test the AI assistant
    hardware = detect_hardware_tier()
    print(f"Hardware tier: {hardware}")
    
    test_config = {
        'vps_ip': '123.45.67.89',
        'family_size': 4,
        'services': ['wireguard', 'adguard']
    }
    
    test_messages = [
        "Hello, I need help setting up my privacy network",
        "What is WireGuard and why do I need it?",
        "How much does this cost?",
        "I'm getting an error during installation"
    ]
    
    for message in test_messages:
        print(f"\nUser: {message}")
        response = get_ai_response(message, test_config)
        print(f"AI: {response}")
