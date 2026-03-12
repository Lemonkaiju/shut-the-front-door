"""
Shut The Front Door! - AdGuard Home Deployment Module
Stage 2: Guided Deployment Application

Module 3: AdGuard Home DNS blocking deployment
Deploys AdGuard Home via Docker for ad and tracker blocking
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any

def deploy_adguard(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deploy AdGuard Home on the specified homelab server.
    
    Args:
        config: Installation configuration containing homelab details
        
    Returns:
        Dict with deployment status and details
    """
    print("🛡️ Starting AdGuard Home deployment...")
    
    result = {
        'module': 'adguard',
        'status': 'started',
        'steps': [],
        'config': {},
        'errors': []
    }
    
    try:
        # Step 1: Validate configuration
        result['steps'].append({
            'name': 'Validating AdGuard configuration',
            'status': 'running'
        })
        
        homelab_ip = config.get('homelab_ip')
        if not homelab_ip:
            raise ValueError("Homelab server IP address is required")
        
        result['steps'][0]['status'] = 'completed'
        
        # Step 2: Test SSH connectivity
        result['steps'].append({
            'name': 'Testing SSH connectivity to homelab',
            'status': 'running'
        })
        
        ssh_test = test_ssh_connection(homelab_ip, config.get('ssh_key'))
        if not ssh_test['success']:
            raise ValueError(f"SSH connection failed: {ssh_test['error']}")
        
        result['steps'][1]['status'] = 'completed'
        
        # Step 3: Install Docker if needed
        result['steps'].append({
            'name': 'Installing Docker on homelab',
            'status': 'running'
        })
        
        docker_install = install_docker(homelab_ip, config.get('ssh_key'))
        if not docker_install['success']:
            raise ValueError(f"Docker installation failed: {docker_install['error']}")
        
        result['steps'][2]['status'] = 'completed'
        
        # Step 4: Deploy AdGuard Home
        result['steps'].append({
            'name': 'Deploying AdGuard Home container',
            'status': 'running'
        })
        
        adguard_deploy = deploy_adguard_container(homelab_ip, config.get('ssh_key'), config)
        if not adguard_deploy['success']:
            raise ValueError(f"AdGuard deployment failed: {adguard_deploy['error']}")
        
        result['steps'][3]['status'] = 'completed'
        result['config'].update(adguard_deploy.get('config', {}))
        
        # Step 5: Configure blocklists
        result['steps'].append({
            'name': 'Configuring recommended blocklists',
            'status': 'running'
        })
        
        blocklist_config = configure_blocklists(homelab_ip, config.get('ssh_key'))
        result['config']['blocklists'] = blocklist_config
        
        result['steps'][4]['status'] = 'completed'
        
        # Step 6: Verify deployment
        result['steps'].append({
            'name': 'Verifying AdGuard Home deployment',
            'status': 'running'
        })
        
        verification = verify_adguard(homelab_ip, adguard_deploy.get('port', 3000))
        if not verification['success']:
            raise ValueError(f"AdGuard verification failed: {verification['error']}")
        
        result['steps'][5]['status'] = 'completed'
        
        # Step 7: Generate setup instructions
        result['steps'].append({
            'name': 'Generating DNS configuration instructions',
            'status': 'running'
        })
        
        dns_instructions = generate_dns_instructions(config, adguard_deploy.get('config', {}))
        result['config']['dns_instructions'] = dns_instructions
        
        result['steps'][6]['status'] = 'completed'
        
        result['status'] = 'completed'
        print("✅ AdGuard Home deployment completed successfully!")
        
    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(str(e))
        print(f"❌ AdGuard Home deployment failed: {e}")
    
    return result

def test_ssh_connection(ip: str, ssh_key: str = None) -> Dict[str, Any]:
    """Test SSH connectivity to the homelab server."""
    try:
        ssh_opts = []
        if ssh_key:
            ssh_opts.extend(['-i', ssh_key])
        
        cmd = ['ssh'] + ssh_opts + [
            '-o', 'ConnectTimeout=10',
            '-o', 'StrictHostKeyChecking=no',
            f'root@{ip}',
            'echo "SSH connection successful"'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        return {
            'success': result.returncode == 0,
            'error': result.stderr if result.returncode != 0 else None
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def install_docker(ip: str, ssh_key: str = None) -> Dict[str, Any]:
    """Install Docker on the homelab server."""
    try:
        ssh_opts = []
        if ssh_key:
            ssh_opts.extend(['-i', ssh_key])
        
        # Docker installation script for Ubuntu/Debian
        docker_script = """
# Check if Docker is already installed
if command -v docker &> /dev/null; then
    echo "Docker is already installed"
    docker --version
else
    # Update package index
    apt-get update

    # Install prerequisites
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Start and enable Docker
    systemctl start docker
    systemctl enable docker

    echo "Docker installation completed"
fi
"""
        
        cmd = ['ssh'] + ssh_opts + [
            '-o', 'ConnectTimeout=30',
            '-o', 'StrictHostKeyChecking=no',
            f'root@{ip}',
            f'bash -c "{docker_script}"'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        return {
            'success': result.returncode == 0,
            'error': result.stderr if result.returncode != 0 else None,
            'output': result.stdout
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def deploy_adguard_container(ip: str, ssh_key: str = None, config: Dict = None) -> Dict[str, Any]:
    """Deploy AdGuard Home container using Docker Compose."""
    try:
        ssh_opts = []
        if ssh_key:
            ssh_opts.extend(['-i', ssh_key])
        
        # Generate AdGuard Home docker-compose.yml
        web_port = config.get('adguard_web_port', 3000)
        
        docker_compose = f"""version: '3.8'
services:
  adguard-home:
    image: adguard/adguardhome:latest
    container_name: adguard-home
    hostname: adguard-home
    volumes:
      - ./adguard-work:/opt/adguardhome/work
      - ./adguard-conf:/opt/adguardhome/conf
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "{web_port}:3000/tcp"
      - "784:784/udp"  # DNS-over-QUIC
      - "853:853/tcp"  # DNS-over-TLS
      - "5443:5443/tcp"  # DNS-over-HTTPS
    environment:
      - TZ=UTC
    restart: unless-stopped
    network_mode: "host"
"""
        
        # Create directory and deploy
        deploy_script = f"""
# Create directories for AdGuard Home
mkdir -p /opt/adguardhome
cd /opt/adguardhome

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
{docker_compose}
EOF

# Create required directories
mkdir -p adguard-work adguard-conf

# Start the container
docker-compose up -d

# Wait for container to initialize
sleep 15

# Check if container is running
docker-compose ps

# Show container logs
docker-compose logs adguard-home
"""
        
        cmd = ['ssh'] + ssh_opts + [
            '-o', 'ConnectTimeout=30',
            '-o', 'StrictHostKeyChecking=no',
            f'root@{ip}',
            f'bash -c "{deploy_script}"'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        return {
            'success': result.returncode == 0,
            'error': result.stderr if result.returncode != 0 else None,
            'output': result.stdout,
            'config': {
                'web_port': web_port,
                'url': f'http://{ip}:{web_port}',
                'dns_port': 53,
                'doh_port': 5443,
                'dot_port': 853,
                'doq_port': 784
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def configure_blocklists(ip: str, ssh_key: str = None) -> Dict[str, Any]:
    """Configure recommended blocklists for AdGuard Home."""
    
    # Recommended blocklists for families
    blocklists = [
        "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter/2_Base.txt",
        "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter/3_Specific.txt",
        "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter/4_Social.txt",
        "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter/14_Trackers.txt",
        "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=adblockplus&showintro=0&mimetype=plaintext",
        "https://raw.githubusercontent.com/hoshsadiq/adblock-nocoin-list/master/nocoin.txt",
        "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
        "https://raw.githubusercontent.com/FadeMind/hosts.extras/master/UncheckyAds/hosts",
        "https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.2o7Net/hosts",
        "https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt",
        "https://raw.githubusercontent.com/AdguardTeam/cname-trackers/master/data/cname-tracker-list.txt"
    ]
    
    return {
        'blocklists': blocklists,
        'enabled_filters': [
            "Base filter",
            "Social media filter", 
            "Tracker filter",
            "Mobile ads filter",
            "Coin mining protection"
        ],
        'custom_rules': [
            "||doubleclick.net^",
            "||googleads.g.doubleclick.net^",
            "||googleadservices.com^",
            "||googlesyndication.com^",
            "||googletagmanager.com^",
            "||googletagservices.com^",
            "||facebook.com^$third-party",
            "||connect.facebook.net^",
            "||amazon-adsystem.com^",
            "||ads.yahoo.com^"
        ]
    }

def verify_adguard(ip: str, port: int = 3000) -> Dict[str, Any]:
    """Verify AdGuard Home is running and accessible."""
    try:
        import socket
        import requests
        
        # Test if web interface is accessible
        try:
            response = requests.get(f'http://{ip}:{port}', timeout=10)
            if response.status_code == 200:
                return {'success': True}
        except requests.RequestException:
            pass
        
        # Test DNS resolution
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [ip]
            resolver.timeout = 5
            resolver.lifetime = 5
            
            result = resolver.resolve('google.com', 'A')
            if result:
                return {'success': True}
        except Exception:
            pass
        
        return {'success': False, 'error': 'AdGuard Home not responding'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def generate_dns_instructions(config: Dict, adguard_config: Dict) -> str:
    """Generate DNS configuration instructions for devices."""
    
    homelab_ip = config.get('homelab_ip')
    router_ip = config.get('router_ip', '192.168.1.1')
    adguard_url = adguard_config.get('url')
    
    instructions = f"""
# DNS Configuration Instructions

## AdGuard Home Setup

### 1. Access AdGuard Home Web Interface
1. Open browser: {adguard_url}
2. Complete initial setup wizard
3. Set admin password

### 2. Configure Blocklists
1. Go to "Filters" → "DNS blocklists"
2. Add the following blocklists:
   - Base filter (AdGuard)
   - Social media filter
   - Tracker filter
   - Coin mining protection
3. Click "Update" and wait for filters to download

### 3. Configure DNS Settings
1. Go to "Settings" → "DNS settings"
2. Upstream DNS servers:
   - 1.1.1.1 (Cloudflare)
   - 8.8.8.8 (Google)
   - 9.9.9.9 (Quad9)
3. Enable "DNSSEC validation"
4. Enable "DNS cache"

### 4. Configure Network Devices

#### For OPNsense Router:
1. Login to OPNsense: https://{router_ip}
2. Navigate to: Services → Unbound DNS → General
3. Set "DNS forwarder" to: {homelab_ip}
4. Enable "DNSSEC Support"
5. Save and apply

#### For Windows Devices:
1. Open Settings → Network & Internet → Ethernet
2. Click "Properties" → "Edit DNS server assignment"
3. Set "Preferred DNS" to: {homelab_ip}
4. Set "Alternate DNS" to: 1.1.1.1

#### For macOS Devices:
1. Open System Preferences → Network
2. Select your connection → Advanced → DNS
3. Add DNS server: {homelab_ip}
4. Remove any other DNS servers

#### For Android Devices:
1. Open Settings → Network & Internet → Private DNS
2. Select "Private DNS provider hostname"
3. Enter: {homelab_ip}

#### For iOS Devices:
1. Open Settings → Wi-Fi → [Your Network] → Configure DNS
2. Select "Manual"
3. Add DNS server: {homelab_ip}

### 5. Test DNS Filtering
1. Open browser and visit: https://ads-block-test.com
2. Should show "ads blocked" message
3. Visit: https://dnsleaktest.com
4. Verify DNS server shows as {homelab_ip}

### 6. Monitor AdGuard Home
1. Check stats at: {adguard_url}
2. Monitor "Dashboard" for blocked requests
3. Review "Query log" for DNS activity
4. Adjust filters as needed

## Advanced Configuration

### Custom Blocking Rules:
1. Go to "Filters" → "Custom filters"
2. Add specific domains to block
3. Use syntax: ||example.com^

### DNS-over-HTTPS:
1. Enable DoH in AdGuard settings
2. Port: 5443
3. Configure clients to use {homelab_ip}:5443

### Per-Device Controls:
1. Go to "Clients" in AdGuard Home
2. Set custom rules per device
3. Configure parental controls

## Troubleshooting

### If DNS isn't working:
- Check AdGuard container is running
- Verify port 53 is not blocked
- Check firewall rules allow DNS traffic

### If ads aren't blocked:
- Verify blocklists are enabled
- Check filter updates are current
- Clear browser cache

### If devices can't connect:
- Verify DNS server IP is correct
- Check network connectivity to {homelab_ip}
- Restart network services
"""
    
    return instructions

if __name__ == '__main__':
    # Test the module
    test_config = {
        'homelab_ip': '192.168.1.100',
        'router_ip': '192.168.1.1',
        'adguard_web_port': 3000
    }
    
    result = deploy_adguard(test_config)
    print(json.dumps(result, indent=2))
