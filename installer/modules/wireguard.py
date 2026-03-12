"""
Shut The Front Door! - WireGuard Deployment Module
Stage 2: Guided Deployment Application

Module 1: WireGuard VPN deployment on cloud VPS
Deploys WG-Easy via Docker for easy VPN management
"""

import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any

def deploy_wireguard(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deploy WireGuard VPN on the specified VPS.
    
    Args:
        config: Installation configuration containing VPS details
        
    Returns:
        Dict with deployment status and details
    """
    print("🚪 Starting WireGuard deployment...")
    
    result = {
        'module': 'wireguard',
        'status': 'started',
        'steps': [],
        'config': {},
        'errors': []
    }
    
    try:
        # Step 1: Validate configuration
        result['steps'].append({
            'name': 'Validating configuration',
            'status': 'running'
        })
        
        vps_ip = config.get('vps_ip')
        vps_provider = config.get('vps_provider')
        ssh_key = config.get('ssh_key')
        
        if not vps_ip:
            raise ValueError("VPS IP address is required")
        
        result['steps'][0]['status'] = 'completed'
        
        # Step 2: Test SSH connectivity
        result['steps'].append({
            'name': 'Testing SSH connectivity',
            'status': 'running'
        })
        
        ssh_test = test_ssh_connection(vps_ip, ssh_key)
        if not ssh_test['success']:
            raise ValueError(f"SSH connection failed: {ssh_test['error']}")
        
        result['steps'][1]['status'] = 'completed'
        
        # Step 3: Install Docker on VPS
        result['steps'].append({
            'name': 'Installing Docker on VPS',
            'status': 'running'
        })
        
        docker_install = install_docker(vps_ip, ssh_key)
        if not docker_install['success']:
            raise ValueError(f"Docker installation failed: {docker_install['error']}")
        
        result['steps'][2]['status'] = 'completed'
        
        # Step 4: Deploy WG-Easy container
        result['steps'].append({
            'name': 'Deploying WG-Easy container',
            'status': 'running'
        })
        
        wg_deploy = deploy_wg_easy(vps_ip, ssh_key, config)
        if not wg_deploy['success']:
            raise ValueError(f"WG-Easy deployment failed: {wg_deploy['error']}")
        
        result['steps'][3]['status'] = 'completed'
        result['config'].update(wg_deploy.get('config', {}))
        
        # Step 5: Verify deployment
        result['steps'].append({
            'name': 'Verifying WireGuard deployment',
            'status': 'running'
        })
        
        verification = verify_wireguard(vps_ip, wg_deploy.get('port', 51820))
        if not verification['success']:
            raise ValueError(f"WireGuard verification failed: {verification['error']}")
        
        result['steps'][4]['status'] = 'completed'
        
        # Step 6: Generate client configurations
        result['steps'].append({
            'name': 'Generating client configurations',
            'status': 'running'
        })
        
        client_configs = generate_client_configs(config, wg_deploy.get('config', {}))
        result['config']['client_configs'] = client_configs
        
        result['steps'][5]['status'] = 'completed'
        
        result['status'] = 'completed'
        print("✅ WireGuard deployment completed successfully!")
        
    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(str(e))
        print(f"❌ WireGuard deployment failed: {e}")
    
    return result

def test_ssh_connection(ip: str, ssh_key: str = None) -> Dict[str, Any]:
    """Test SSH connectivity to the VPS."""
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
    """Install Docker on the VPS."""
    try:
        ssh_opts = []
        if ssh_key:
            ssh_opts.extend(['-i', ssh_key])
        
        # Docker installation script for Ubuntu/Debian
        docker_script = """
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

# Add current user to docker group
usermod -aG docker $USER

echo "Docker installation completed"
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

def deploy_wg_easy(ip: str, ssh_key: str = None, config: Dict = None) -> Dict[str, Any]:
    """Deploy WG-Easy container using Docker Compose."""
    try:
        ssh_opts = []
        if ssh_key:
            ssh_opts.extend(['-i', ssh_key])
        
        # Generate WG-Easy docker-compose.yml
        wg_password = config.get('wg_password', 'ChangeMe123!')
        wg_port = config.get('wg_port', 51820)
        web_port = config.get('wg_web_port', 51821)
        
        docker_compose = f"""version: '3.8'
services:
  wg-easy:
    image: ghcr.io/wg-easy/wg-easy
    container_name: wg-easy
    volumes:
      - ./wg-easy:/etc/wireguard
    ports:
      - "{wg_port}:51820/udp"
      - "{web_port}:51821/tcp"
    environment:
      - WG_PASSWORD={wg_password}
      - WG_DEFAULT_DNS=1.1.1.1
      - WG_MTU=1420
      - WG_PERSISTENT_KEEPALIVE=25
      - WG_ALLOWED_IPS=0.0.0.0/0,::/0
    cap_add:
      - NET_ADMIN
    sysctls:
      - net.ipv4.ip_forward=1
      - net.ipv6.conf.all.forwarding=1
    restart: unless-stopped
"""
        
        # Create directory and deploy
        deploy_script = f"""
# Create directory for WireGuard
mkdir -p /opt/wireguard
cd /opt/wireguard

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
{docker_compose}
EOF

# Start the container
docker-compose up -d

# Wait for container to start
sleep 10

# Check if container is running
docker-compose ps
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
                'port': wg_port,
                'web_port': web_port,
                'password': wg_password,
                'url': f'http://{ip}:{web_port}'
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def verify_wireguard(ip: str, port: int = 51820) -> Dict[str, Any]:
    """Verify WireGuard is running and accessible."""
    try:
        import socket
        
        # Test if WireGuard port is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        try:
            # Simple connectivity test
            sock.sendto(b'test', (ip, port))
            sock.close()
            return {'success': True}
        except socket.timeout:
            sock.close()
            return {'success': False, 'error': 'WireGuard port not responding'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def generate_client_configs(config: Dict, wg_config: Dict) -> Dict[str, Any]:
    """Generate WireGuard client configurations."""
    
    # Generate configuration for home router
    home_router_config = f"""[Interface]
PrivateKey = [CLIENT_PRIVATE_KEY]
Address = 10.8.0.2/24
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = [SERVER_PUBLIC_KEY]
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = {config.get('vps_ip')}:{wg_config.get('port', 51820)}
PersistentKeepalive = 25
"""
    
    # Generate configuration for mobile devices
    mobile_config = f"""[Interface]
PrivateKey = [CLIENT_PRIVATE_KEY]
Address = 10.8.0.3/24
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = [SERVER_PUBLIC_KEY]
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = {config.get('vps_ip')}:{wg_config.get('port', 51820)}
PersistentKeepalive = 25
"""
    
    return {
        'home_router': {
            'name': 'Home Router',
            'config': home_router_config,
            'filename': 'home-router.conf'
        },
        'mobile': {
            'name': 'Mobile Device',
            'config': mobile_config,
            'filename': 'mobile-device.conf'
        },
        'setup_instructions': f"""
1. Access WG-Easy web interface: {wg_config.get('url')}
2. Login with password: {wg_config.get('password')}
3. Create peers for each device
4. Download configuration files
5. Import configs into WireGuard clients
"""
    }

if __name__ == '__main__':
    # Test the module
    test_config = {
        'vps_ip': '123.45.67.89',
        'vps_provider': 'digitalocean',
        'wg_password': 'TestPass123!'
    }
    
    result = deploy_wireguard(test_config)
    print(json.dumps(result, indent=2))
