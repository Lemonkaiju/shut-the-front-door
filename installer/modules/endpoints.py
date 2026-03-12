"""
Shut The Front Door! - Endpoint Hardening Module
Stage 2: Guided Deployment Application

Module 6: Family device configuration and hardening
Provides guidance for setting up privacy-focused endpoints
"""

import json
from pathlib import Path
from typing import Dict, Any

def deploy_endpoints(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Configure family devices with privacy-focused settings.
    
    Args:
        config: Installation configuration containing device details
        
    Returns:
        Dict with deployment status and details
    """
    print("💻 Starting endpoint configuration...")
    
    result = {
        'module': 'endpoints',
        'status': 'started',
        'steps': [],
        'config': {},
        'errors': []
    }
    
    try:
        # Step 1: Validate configuration
        result['steps'].append({
            'name': 'Validating endpoint configuration',
            'status': 'running'
        })
        
        family_size = config.get('family_size', 4)
        domain = config.get('domain', 'family.local')
        
        result['steps'][0]['status'] = 'completed'
        
        # Step 2: Generate OS recommendations
        result['steps'].append({
            'name': 'Generating OS recommendations',
            'status': 'running'
        })
        
        os_recommendations = generate_os_recommendations(config)
        result['config']['os_recommendations'] = os_recommendations
        
        result['steps'][1]['status'] = 'completed'
        
        # Step 3: Create browser configuration guides
        result['steps'].append({
            'name': 'Creating browser configuration guides',
            'status': 'running'
        })
        
        browser_configs = generate_browser_configs(config)
        result['config']['browser_configs'] = browser_configs
        
        result['steps'][2]['status'] = 'completed'
        
        # Step 4: Generate DNS/VPN setup instructions
        result['steps'].append({
            'name': 'Generating DNS/VPN setup instructions',
            'status': 'running'
        })
        
        network_configs = generate_network_configs(config)
        result['config']['network_configs'] = network_configs
        
        result['steps'][3]['status'] = 'completed'
        
        # Step 5: Create parental control setup
        result['steps'].append({
            'name': 'Creating parental control setup guides',
            'status': 'running'
        })
        
        parental_controls = generate_parental_controls(config)
        result['config']['parental_controls'] = parental_controls
        
        result['steps'][4]['status'] = 'completed'
        
        # Step 6: Generate security hardening guide
        result['steps'].append({
            'name': 'Generating security hardening guide',
            'status': 'running'
        })
        
        security_hardening = generate_security_hardening(config)
        result['config']['security_hardening'] = security_hardening
        
        result['steps'][5]['status'] = 'completed'
        
        # Step 7: Create device setup checklist
        result['steps'].append({
            'name': 'Creating device setup checklist',
            'status': 'running'
        })
        
        setup_checklist = generate_setup_checklist(config)
        result['config']['setup_checklist'] = setup_checklist
        
        result['steps'][6]['status'] = 'completed'
        
        # Step 8: Generate agentic AI guide (advanced users)
        result['steps'].append({
            'name': 'Generating agentic AI engineering guide',
            'status': 'running'
        })
        
        agentic_ai_guide = generate_agentic_ai_guide(config)
        result['config']['agentic_ai_guide'] = agentic_ai_guide
        
        result['steps'][7]['status'] = 'completed'
        
        result['status'] = 'completed'
        print("✅ Endpoint configuration completed successfully!")
        
    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(str(e))
        print(f"❌ Endpoint configuration failed: {e}")
    
    return result

def generate_os_recommendations(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate OS recommendations for family devices."""
    
    family_size = config.get('family_size', 4)
    
    recommendations = {
        'primary_recommendation': {
            'name': 'Bazzite',
            'description': 'Fedora-based immutable Linux distribution with gaming focus',
            'pros': [
                'Immutable base system (very secure)',
                'Automatic updates',
                'Steam and gaming pre-configured',
                'Flatpak app support',
                'No telemetry',
                'Family-friendly interface'
            ],
            'cons': [
                'Learning curve for Windows users',
                'Some Windows software may not work',
                'Limited hardware support compared to major distros'
            ],
            'suitable_for': ['Gaming computers', 'Desktop workstations', 'Family computers']
        },
        'alternative_recommendations': [
            {
                'name': 'Linux Mint',
                'description': 'Ubuntu-based with traditional desktop interface',
                'pros': ['Windows-like interface', 'Large software repository', 'Good hardware support'],
                'cons': ['Not immutable', 'Ubuntu base may have some telemetry'],
                'suitable_for': ['Beginners', 'Older hardware', 'Transition from Windows']
            },
            {
                'name': 'Fedora Workstation',
                'description': 'Cutting-edge Linux with focus on free software',
                'pros': ['Latest software', 'Strong security', 'Good developer tools'],
                'cons': ['Faster release cycle', 'Some proprietary software requires setup'],
                'suitable_for': ['Technical users', 'Developers', 'Security-conscious users']
            }
        ],
        'installation_guide': {
            'bazzite': {
                'download_url': 'https://bazzite.gg/',
                'requirements': [
                    '64-bit x86 processor',
                    '4GB RAM minimum (8GB recommended)',
                    '20GB storage minimum (50GB recommended)',
                    'UEFI firmware recommended'
                ],
                'installation_steps': [
                    'Download Bazzite ISO from official website',
                    'Create bootable USB using Rufus (Windows) or balenaEtcher',
                    'Boot from USB and follow installation wizard',
                    'Create user accounts for each family member',
                    'Connect to family network and configure DNS'
                ],
                'browser_setup': [
                    'Install Mullvad Browser: flatpak install flathub net.mullvad.MullvadBrowser',
                    'Launch Mullvad Browser - no configuration needed',
                    'Install LibreWolf for advanced users: flatpak install flathub io.gitlab.librewolf-community',
                    'Configure DNS settings to use family DNS server'
                ]
            }
        }
    }
    
    return recommendations

def generate_browser_configs(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate privacy-focused browser configurations."""
    
    configs = {
        'primary_browser': {
            'name': 'Mullvad Browser',
            'reason': 'Developed by Tor Project team with anti-fingerprinting built-in',
            'features': [
                'Anti-fingerprinting by default',
                'Letterboxing to hide screen resolution',
                'Windows user agent spoofing',
                'Canvas and WebGL randomization',
                'Standard font set spoofing',
                'No telemetry or data collection',
                'Hardened security settings'
            ]
        },
        'secondary_browser': {
            'name': 'LibreWolf',
            'reason': 'Firefox fork with enhanced privacy and security for power users',
            'features': [
                'uBlock Origin pre-installed',
                'Enhanced tracking protection',
                'privacy.resistFingerprinting enabled',
                'No telemetry',
                'Security hardening',
                'Regular security updates'
            ]
        },
        'configurations': {
            'mullvad': {
                'privacy_settings': [
                    'All anti-fingerprinting enabled by default',
                    'Letterboxing active (grey bars hide resolution)',
                    'Windows user agent spoofing enabled',
                    'Canvas and WebGL randomization active',
                    'Font spoofing to standard Windows set',
                    'Timezone spoofing to common timezone'
                ],
                'security_settings': [
                    'HTTPS-Only Mode enabled',
                    'Third-party cookies blocked',
                    'WebRTC disabled to prevent IP leaks',
                    'Safe browsing disabled (uses local protection)',
                    'No telemetry or data collection'
                ],
                'notes': [
                    'Zero configuration required - hardened out of the box',
                    'Perfect for kids and non-technical users',
                    'Developed by Tor Project team',
                    'Appears as Windows Firefox to websites'
                ]
            },
            'librewolf': {
                'privacy_settings': [
                    'Enable "Strict Enhanced Tracking Protection"',
                    'Set "Delete cookies and site data when closed"',
                    'Disable "Telemetry"',
                    'Set "DNS over HTTPS" to custom (family DNS server)',
                    'Enable "Container tabs" for different activities'
                ],
                'security_settings': [
                    'Enable "HTTPS-Only Mode"',
                    'Block all third-party cookies',
                    'Disable "WebRTC" to prevent IP leaks',
                    'Set "Sandbox" level to high',
                    'Enable "Firefox Monitor" for breach alerts'
                ],
                'notes': [
                    'For power users who want Firefox experience',
                    'May cause some sites to break due to fingerprinting resistance',
                    'Requires occasional configuration adjustments'
                ]
            }
        },
        'installation_commands': {
            'bazzite': {
                'mullvad': 'flatpak install flathub net.mullvad.MullvadBrowser',
                'librewolf': 'flatpak install flathub io.gitlab.librewolf-community'
            },
            'linux_mint': {
                'mullvad': 'wget -qO- https://mullvad.net/en/download/browser/linux/x64/ | tar -xvzf - && sudo mv mullvad-browser /opt/',
                'librewolf': 'sudo add-apt-repository ppa:librewolf/ppa && sudo apt update && sudo apt install librewolf'
            }
        }
    }
    
    return configs

def generate_network_configs(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate network configuration instructions for devices."""
    
    homelab_ip = config.get('homelab_ip', '192.168.1.100')
    router_ip = config.get('router_ip', '192.168.1.1')
    vps_ip = config.get('vps_ip')
    domain = config.get('domain', 'family.local')
    
    configs = {
        'dns_configuration': {
            'primary_dns': homelab_ip,
            'secondary_dns': '1.1.1.1',
            'description': 'Use family DNS server for ad/tracker blocking',
            'setup_instructions': {
                'linux': {
                    'network_manager': [
                        'Open Settings → Network',
                        'Select your connection',
                        'Click "Gear" → IPv4',
                        'Set DNS to: ' + homelab_ip + ', 1.1.1.1',
                        'Save and reconnect'
                    ],
                    'cli': [
                        'sudo nano /etc/systemd/resolved.conf',
                        'Add: DNS=' + homelab_ip + ' 1.1.1.1',
                        'sudo systemctl restart systemd-resolved'
                    ]
                },
                'windows': {
                    'gui': [
                        'Open Settings → Network & Internet',
                        'Click "Properties" on your connection',
                        'Edit "DNS server assignment"',
                        'Set "Preferred DNS" to: ' + homelab_ip,
                        'Set "Alternate DNS" to: 1.1.1.1'
                    ],
                    'powershell': [
                        'Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses "' + homelab_ip + ',1.1.1.1"'
                    ]
                }
            }
        },
        'wireguard_configuration': {
            'description': 'Connect to family VPN for privacy and bypassing restrictions',
            'setup_instructions': {
                'linux': {
                    'installation': 'sudo apt install wireguard-tools',
                    'configuration': [
                        'Download config from WG-Easy web interface',
                        'Copy to /etc/wireguard/family.conf',
                        'sudo wg-quick up family',
                        'sudo systemctl enable wg-quick@family'
                    ]
                },
                'windows': {
                    'installation': 'Download and install WireGuard from wireguard.com',
                    'configuration': [
                        'Download config from WG-Easy web interface',
                        'Import config into WireGuard client',
                        'Click "Activate" to connect'
                    ]
                },
                'mobile': {
                    'android': 'Install WireGuard from Google Play, import config',
                    'ios': 'Install WireGuard from App Store, import config'
                }
            }
        },
        'verification_tests': {
            'dns_test': [
                'Open browser and visit: https://dnsleaktest.com',
                'Verify DNS shows as: ' + homelab_ip,
                'Check that ads are blocked on test sites'
            ],
            'vpn_test': [
                'Visit: https://ipleak.net/',
                'Verify IP shows as VPS: ' + (vps_ip or 'configured'),
                'Check DNS leak protection is working'
            ]
        }
    }
    
    return configs

def generate_parental_controls(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate parental control setup guides."""
    
    family_size = config.get('family_size', 4)
    
    controls = {
        'time_management': {
            'tool': 'Timekpr-nExT',
            'description': 'Control screen time for child accounts',
            'installation': 'sudo apt install timekpr-next',
            'configuration': {
                'daily_limits': {
                    'weekdays': '2 hours',
                    'weekends': '4 hours',
                    'bedtime': '21:00',
                    'wake_time': '07:00'
                },
                'time_banks': {
                    'description': 'Allow extra time for homework or special activities',
                    'reset_frequency': 'weekly'
                }
            }
        },
        'content_filtering': {
            'dns_level': [
                'AdGuard Home blocklists',
                'Custom domain blocking',
                'Safe search enforcement'
            ],
            'browser_level': [
                'Safe search in all search engines',
                'Block explicit content',
                'Disable incognito mode for children'
            ],
            'application_level': [
                'Age-appropriate software restrictions',
                'App store purchase controls',
                'Social media time limits'
            ]
        },
        'monitoring': {
            'activity_logs': {
                'description': 'Review internet activity and usage patterns',
                'frequency': 'Weekly review by parents',
                'privacy_respect': 'Respect child privacy while ensuring safety'
            },
            'alerts': {
                'suspicious_activity': 'Alert for unusual access patterns',
                'time_limit_exceeded': 'Notify when limits are reached',
                'blocked_content_attempts': 'Log attempts to access blocked content'
            }
        },
        'child_accounts_setup': {
            'account_types': [
                {
                    'type': 'Young Children (6-10)',
                    'restrictions': ['Limited app access', 'Strict content filtering', 'Shorter time limits'],
                    'supervision': 'Full parental supervision required'
                },
                {
                    'type': 'Pre-teens (11-13)',
                    'restrictions': ['Educational content priority', 'Social media limits', 'Extended time with approval'],
                    'supervision': 'Guided access with some autonomy'
                },
                {
                    'type': 'Teens (14+)',
                    'restrictions': ['Responsible use education', 'Privacy boundaries', 'Trust-based system'],
                    'supervision': 'Monitoring with privacy respect'
                }
            ]
        }
    }
    
    return controls

def generate_security_hardening(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate security hardening guides for family devices."""
    
    hardening = {
        'system_security': {
            'user_accounts': [
                'Create separate accounts for each family member',
                'Use strong, unique passwords',
                'Enable two-factor authentication where available',
                'Limit admin access to parents only'
            ],
            'updates': [
                'Enable automatic security updates',
                'Update software regularly',
                'Keep browser extensions updated',
                'Review update logs'
            ],
            'firewall': [
                'Enable system firewall',
                'Block unnecessary ports',
                'Allow only required services',
                'Monitor firewall logs'
            ]
        },
        'privacy_protection': {
            'data_minimization': [
                'Disable telemetry and data collection',
                'Use privacy-respecting alternatives',
                'Clear browsing data regularly',
                'Review app permissions'
            ],
            'encryption': [
                'Enable full disk encryption',
                'Use encrypted messaging apps',
                'Encrypt sensitive files',
                'Backup encryption keys securely'
            ],
            'network_privacy': [
                'Use VPN when on public networks',
                'Disable location services when not needed',
                'Use DNS-over-HTTPS',
                'Block tracking cookies'
            ],
            'fingerprinting_protection': [
                'Use Mullvad Browser for all family members',
                'Enable letterboxing to hide screen resolution',
                'Block canvas and WebGL fingerprinting',
                'Spoof user agent to common browser',
                'Use standard font sets instead of system fonts',
                'Randomize timezone and language settings'
            ]
        },
        'malware_protection': {
            'prevention': [
                'Install reputable antivirus (Linux: ClamAV)',
                'Scan downloads before opening',
                'Avoid suspicious websites',
                'Use ad blockers'
            ],
            'detection': [
                'Regular system scans',
                'Monitor unusual activity',
                'Review system logs',
                'Check for unauthorized changes'
            ],
            'response': [
                'Isolate infected systems',
                'Backup important data',
                'Clean or reinstall systems',
                'Review security practices'
            ]
        },
        'backup_strategy': {
            '321_rule': [
                '3 copies of important data',
                '2 different storage types',
                '1 copy off-site (or separate location)'
            ],
            'automation': [
                'Set up automatic backups',
                'Test backup restoration',
                'Rotate backup media',
                'Document backup procedures'
            ],
            'encryption': [
                'Encrypt backup data',
                'Store encryption keys separately',
                'Use strong encryption algorithms',
                'Regularly update encryption methods'
            ]
        }
    }
    
    return hardening

def generate_setup_checklist(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive device setup checklist."""
    
    checklist = {
        'pre_setup': [
            'Backup current system and data',
            'Create recovery media',
            'Document current software licenses',
            'List important applications and data',
            'Check hardware compatibility'
        ],
        'os_installation': [
            'Download recommended OS (Bazzite)',
            'Create bootable installation media',
            'Verify media integrity',
            'Backup BIOS/UEFI settings',
            'Document hardware configuration'
        ],
        'initial_setup': [
            'Install OS with default privacy settings',
            'Create admin account for parents',
            'Create standard accounts for children',
            'Set strong passwords for all accounts',
            'Configure basic network settings'
        ],
        'network_configuration': [
            'Connect to family network',
            'Configure DNS to use family server',
            'Test internet connectivity',
            'Verify DNS filtering is working',
            'Set up WireGuard VPN connection'
        ],
        'software_installation': [
            'Install Brave browser',
            'Install LibreWolf (alternative browser)',
            'Install LibreOffice',
            'Install Timekpr-nExT for parental controls',
            'Install required Flatpak applications'
        ],
        'browser_configuration': [
            'Configure privacy settings in Brave',
            'Install essential extensions (uBlock Origin)',
            'Set default search engine to DuckDuckGo',
            'Configure bookmark sync (if desired)',
            'Test ad blocking functionality'
        ],
        'parental_controls': [
            'Configure Timekpr-nExT limits for children',
            'Set up content filtering',
            'Configure application restrictions',
            'Set up monitoring and alerts',
            'Test all parental control features'
        ],
        'security_hardening': [
            'Enable system firewall',
            'Configure automatic updates',
            'Set up antivirus scanning',
            'Enable disk encryption',
            'Configure user permissions'
        ],
        'backup_setup': [
            'Configure automatic backups',
            'Test backup restoration',
            'Set up cloud backup (if desired)',
            'Document backup procedures',
            'Schedule regular backup testing'
        ],
        'verification_testing': [
            'Test all user accounts can login',
            'Verify internet access works properly',
            'Test DNS filtering is blocking ads',
            'Test VPN connection and IP masking',
            'Verify parental controls are working',
            'Test backup and restore procedures'
        ],
        'documentation': [
            'Document all account credentials',
            'Create setup guide for family members',
            'Document troubleshooting procedures',
            'Create emergency contact information',
            'Schedule regular maintenance tasks'
        ],
        'family_training': [
            'Train parents on admin functions',
            'Teach children about internet safety',
            'Demonstrate proper software usage',
            'Explain privacy and security practices',
            'Create family technology agreement'
        ]
    }
    
    return checklist

def generate_agentic_ai_guide(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate setup instructions for an agentic AI coding assistant (advanced users)."""
    
    return {
        'title': 'Agentic AI Engineering Setup',
        'audience': 'Advanced technical users',
        'description': (
            'Run a fully local AI coding assistant — no cloud, no telemetry. '
            'Your code and prompts never leave your machine.'
        ),
        'requirements': {
            'hardware': {
                'minimum': '16 GB RAM, modern quad-core CPU',
                'recommended': '32 GB RAM, GPU with 8 GB+ VRAM (NVIDIA/AMD)',
                'storage': '40 GB free for models'
            },
            'os': [
                'Linux (Bazzite / LemonKaijuOS recommended)',
                'Windows 11 with WSL2',
                'macOS 13+'
            ],
            'software': [
                'Ollama (already installed by AI Setup step)',
                'Python 3.11+',
                'Git',
                'Docker (optional, for agent orchestration)'
            ]
        },
        'recommended_models': [
            {
                'name': 'qwen2.5-coder:14b',
                'vram_gb': 9,
                'use_case': 'General coding, best balance of speed and quality',
                'pull_command': 'ollama pull qwen2.5-coder:14b',
                'recommended_for': 'most_users'
            },
            {
                'name': 'deepseek-coder-v2:16b',
                'vram_gb': 10,
                'use_case': 'Advanced coding, complex refactors',
                'pull_command': 'ollama pull deepseek-coder-v2:16b',
                'recommended_for': 'power_users'
            },
            {
                'name': 'llama3.1:8b',
                'vram_gb': 5,
                'use_case': 'Low-spec fallback, general assistant',
                'pull_command': 'ollama pull llama3.1:8b',
                'recommended_for': 'low_spec'
            },
            {
                'name': 'codellama:13b',
                'vram_gb': 8,
                'use_case': 'Code completion and generation',
                'pull_command': 'ollama pull codellama:13b',
                'recommended_for': 'code_completion'
            }
        ],
        'setup_steps': [
            {
                'step': 1,
                'title': 'Verify Ollama is running',
                'commands': ['ollama serve', 'curl http://localhost:11434/api/tags'],
                'notes': 'Should return a JSON list of installed models'
            },
            {
                'step': 2,
                'title': 'Pull a coding model',
                'commands': ['ollama pull qwen2.5-coder:14b'],
                'notes': 'This downloads ~9 GB — allow 15-30 minutes on a fast connection'
            },
            {
                'step': 3,
                'title': 'Install an AI-native IDE',
                'options': [
                    {
                        'name': 'Windsurf',
                        'url': 'https://windsurf.ai',
                        'notes': 'Agentic IDE with Cascade AI — point to localhost:11434 for local model'
                    },
                    {
                        'name': 'Cursor',
                        'url': 'https://www.cursor.so',
                        'notes': 'VS Code fork with AI — supports custom Ollama backend'
                    },
                    {
                        'name': 'Continue.dev',
                        'url': 'https://continue.dev',
                        'notes': 'Open-source VS Code extension with Ollama support, fully local'
                    }
                ]
            },
            {
                'step': 4,
                'title': 'Configure IDE to use local Ollama',
                'commands': [],
                'config_example': {
                    'ollama_api_base': 'http://localhost:11434',
                    'model': 'qwen2.5-coder:14b',
                    'context_length': 8192
                },
                'notes': 'In Windsurf/Cursor, set the model provider to Ollama and base URL to http://localhost:11434'
            },
            {
                'step': 5,
                'title': 'Install agent frameworks (optional)',
                'commands': [
                    'pip install langchain langchain-community',
                    'pip install autogen-agentchat',
                    'pip install open-interpreter'
                ],
                'notes': 'These allow building autonomous agents that can write and execute code'
            },
            {
                'step': 6,
                'title': 'Set up Antigravity or custom agent',
                'commands': [
                    'git clone <your-agent-repo>',
                    'pip install -r requirements.txt',
                    'python agent.py --model qwen2.5-coder:14b --ollama-url http://localhost:11434'
                ],
                'notes': 'Antigravity and similar agents connect to your local Ollama instance'
            }
        ],
        'privacy_notes': [
            'All inference runs locally — no API calls to OpenAI, Anthropic, or Google',
            'Your code, prompts, and completions never leave your machine',
            'Model weights are stored in ~/.ollama/models',
            'No usage telemetry when using Ollama directly',
            'For maximum isolation, block Ollama from internet access in OPNsense after model download'
        ],
        'performance_tips': [
            'Enable GPU acceleration: Ollama detects NVIDIA/AMD/Apple Silicon automatically',
            'Increase context window for large codebases via OLLAMA_CONTEXT_LENGTH env var',
            'Run ollama with OLLAMA_NUM_PARALLEL=2 to serve multiple IDE requests',
            'Use quantized models (Q4_K_M) for 30% less VRAM with minimal quality loss',
            'SSD storage significantly reduces model load times'
        ],
        'troubleshooting': {
            'ollama_not_found': 'Run: curl -fsSL https://ollama.ai/install.sh | sh',
            'gpu_not_detected': 'Install NVIDIA drivers and CUDA toolkit, then restart Ollama',
            'out_of_memory': 'Switch to a smaller model (llama3.1:8b) or enable CPU offloading',
            'slow_responses': 'Ensure GPU acceleration is active: ollama ps should show GPU usage',
            'ide_cant_connect': 'Verify Ollama is running on http://localhost:11434, check firewall'
        }
    }


if __name__ == '__main__':
    # Test the module
    test_config = {
        'family_size': 4,
        'domain': 'family.local',
        'homelab_ip': '192.168.1.100',
        'router_ip': '192.168.1.1',
        'vps_ip': '123.45.67.89'
    }
    
    result = deploy_endpoints(test_config)
    print(json.dumps(result, indent=2))
