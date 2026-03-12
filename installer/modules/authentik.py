"""
Shut The Front Door! - Authentik Deployment Module
Stage 2: Guided Deployment Application

Module 4: Authentik SSO deployment
Deploys Authentik via Docker for centralized family authentication
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any

def deploy_authentik(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deploy Authentik SSO on the specified homelab server.
    
    Args:
        config: Installation configuration containing family details
        
    Returns:
        Dict with deployment status and details
    """
    print("👨‍👩‍👧‍👦 Starting Authentik SSO deployment...")
    
    result = {
        'module': 'authentik',
        'status': 'started',
        'steps': [],
        'config': {},
        'errors': []
    }
    
    try:
        # Step 1: Validate configuration
        result['steps'].append({
            'name': 'Validating Authentik configuration',
            'status': 'running'
        })
        
        homelab_ip = config.get('homelab_ip')
        family_size = config.get('family_size', 4)
        domain = config.get('domain', 'family.local')
        
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
        
        # Step 3: Deploy Authentik container
        result['steps'].append({
            'name': 'Deploying Authentik container',
            'status': 'running'
        })
        
        authentik_deploy = deploy_authentik_container(homelab_ip, config.get('ssh_key'), config)
        if not authentik_deploy['success']:
            raise ValueError(f"Authentik deployment failed: {authentik_deploy['error']}")
        
        result['steps'][2]['status'] = 'completed'
        result['config'].update(authentik_deploy.get('config', {}))
        
        # Step 4: Wait for initialization
        result['steps'].append({
            'name': 'Waiting for Authentik initialization',
            'status': 'running'
        })
        
        # Give Authentik time to initialize
        import time
        time.sleep(30)
        
        result['steps'][3]['status'] = 'completed'
        
        # Step 5: Create family accounts
        result['steps'].append({
            'name': 'Creating family accounts',
            'status': 'running'
        })
        
        family_accounts = create_family_accounts(config, authentik_deploy.get('config', {}))
        result['config']['family_accounts'] = family_accounts
        
        result['steps'][4]['status'] = 'completed'
        
        # Step 6: Configure OIDC for Nextcloud
        result['steps'].append({
            'name': 'Configuring OIDC for Nextcloud',
            'status': 'running'
        })
        
        oidc_config = configure_oidc(config, authentik_deploy.get('config', {}))
        result['config']['oidc'] = oidc_config
        
        result['steps'][5]['status'] = 'completed'
        
        # Step 7: Verify deployment
        result['steps'].append({
            'name': 'Verifying Authentik deployment',
            'status': 'running'
        })
        
        verification = verify_authentik(homelab_ip, authentik_deploy.get('web_port', 9000))
        if not verification['success']:
            raise ValueError(f"Authentik verification failed: {verification['error']}")
        
        result['steps'][6]['status'] = 'completed'
        
        # Step 8: Generate setup instructions
        result['steps'].append({
            'name': 'Generating account setup instructions',
            'status': 'running'
        })
        
        setup_instructions = generate_setup_instructions(config, authentik_deploy.get('config', {}))
        result['config']['setup_instructions'] = setup_instructions
        
        result['steps'][7]['status'] = 'completed'
        
        result['status'] = 'completed'
        print("✅ Authentik SSO deployment completed successfully!")
        
    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(str(e))
        print(f"❌ Authentik SSO deployment failed: {e}")
    
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

def deploy_authentik_container(ip: str, ssh_key: str = None, config: Dict = None) -> Dict[str, Any]:
    """Deploy Authentik container using Docker Compose."""
    try:
        ssh_opts = []
        if ssh_key:
            ssh_opts.extend(['-i', ssh_key])
        
        # Generate Authentik docker-compose.yml
        domain = config.get('domain', 'family.local')
        web_port = config.get('authentik_web_port', 9000)
        secret_key = generate_random_password(50)
        
        docker_compose = f"""version: '3.8'

services:
  postgresql:
    image: postgres:14
    container_name: authentik-postgresql
    restart: unless-stopped
    volumes:
      - ./authentik-postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=authentik
      - POSTGRES_PASSWORD={generate_random_password(32)}
      - POSTGRES_DB=authentik
    networks:
      - authentik

  redis:
    image: redis:alpine
    container_name: authentik-redis
    restart: unless-stopped
    networks:
      - authentik

  authentik-server:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik-server
    restart: unless-stopped
    depends_on:
      - postgresql
      - redis
    volumes:
      - ./authentik-media:/media
      - ./authentik-templates:/templates
    environment:
      - AUTHENTIK_SECRET_KEY={secret_key}
      - AUTHENTIK_POSTGRESQL__HOST=postgresql
      - AUTHENTIK_POSTGRESQL__USER=authentik
      - AUTHENTIK_POSTGRESQL__NAME=authentik
      - AUTHENTIK_POSTGRESQL__PASSWORD={generate_random_password(32)}
      - AUTHENTIK_REDIS__HOST=redis
    ports:
      - "{web_port}:9000"
      - "9443:9443"
    networks:
      - authentik

  authentik-worker:
    image: ghcr.io/goauthentik/server:latest
    container_name: authentik-worker
    restart: unless-stopped
    depends_on:
      - postgresql
      - redis
    volumes:
      - ./authentik-media:/media
      - ./authentik-templates:/templates
    environment:
      - AUTHENTIK_SECRET_KEY={secret_key}
      - AUTHENTIK_POSTGRESQL__HOST=postgresql
      - AUTHENTIK_POSTGRESQL__USER=authentik
      - AUTHENTIK_POSTGRESQL__NAME=authentik
      - AUTHENTIK_POSTGRESQL__PASSWORD={generate_random_password(32)}
      - AUTHENTIK_REDIS__HOST=redis
    command: worker
    networks:
      - authentik

networks:
  authentik:
    driver: bridge
"""
        
        # Create directory and deploy
        deploy_script = f"""
# Create directories for Authentik
mkdir -p /opt/authentik
cd /opt/authentik

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
{docker_compose}
EOF

# Create required directories
mkdir -p authentik-postgres authentik-media authentik-templates

# Start the containers
docker-compose up -d

# Wait for containers to initialize
sleep 30

# Check container status
docker-compose ps

# Show initial logs
docker-compose logs authentik-server | tail -20
"""
        
        cmd = ['ssh'] + ssh_opts + [
            '-o', 'ConnectTimeout=30',
            '-o', 'StrictHostKeyChecking=no',
            f'root@{ip}',
            f'bash -c "{deploy_script}"'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        return {
            'success': result.returncode == 0,
            'error': result.stderr if result.returncode != 0 else None,
            'output': result.stdout,
            'config': {
                'web_port': web_port,
                'url': f'http://{ip}:{web_port}',
                'https_url': f'https://{ip}:9443',
                'domain': domain,
                'secret_key': secret_key
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def create_family_accounts(config: Dict, authentik_config: Dict) -> Dict[str, Any]:
    """Create family user accounts structure."""
    
    family_size = config.get('family_size', 4)
    domain = config.get('domain', 'family.local')
    
    # Generate family account structure
    accounts = {
        'parents': [
            {
                'username': 'parent1',
                'email': f'parent1@{domain}',
                'name': 'Parent 1',
                'role': 'admin',
                'password': generate_random_password(12),
                'mfa_enabled': True
            },
            {
                'username': 'parent2', 
                'email': f'parent2@{domain}',
                'name': 'Parent 2',
                'role': 'admin',
                'password': generate_random_password(12),
                'mfa_enabled': True
            }
        ],
        'children': []
    }
    
    # Create child accounts
    for i in range(max(0, family_size - 2)):
        child_num = i + 1
        accounts['children'].append({
            'username': f'child{child_num}',
            'email': f'child{child_num}@{domain}',
            'name': f'Child {child_num}',
            'role': 'user',
            'password': generate_random_password(8),
            'mfa_enabled': False,
            'restricted_access': True
        })
    
    return accounts

def configure_oidc(config: Dict, authentik_config: Dict) -> Dict[str, Any]:
    """Configure OIDC settings for Nextcloud integration."""
    
    domain = config.get('domain', 'family.local')
    
    oidc_config = {
        'provider_name': 'Nextcloud',
        'client_id': 'nextcloud-oidc',
        'client_secret': generate_random_password(32),
        'redirect_uris': [
            f'http://nextcloud.{domain}/apps/oidclogin/oidc/',
            f'http://nextcloud.{domain}/login'
        ],
        'scopes': ['openid', 'profile', 'email'],
        'authorization_flow': 'default-authorization-flow',
        'property_mappings': {
            'username': 'username',
            'email': 'email',
            'name': 'name'
        }
    }
    
    return oidc_config

def verify_authentik(ip: str, port: int = 9000) -> Dict[str, Any]:
    """Verify Authentik is running and accessible."""
    try:
        import requests
        
        # Test if web interface is accessible
        try:
            response = requests.get(f'http://{ip}:{port}', timeout=10, allow_redirects=True)
            if response.status_code in [200, 302]:
                return {'success': True}
        except requests.RequestException:
            pass
        
        return {'success': False, 'error': 'Authentik web interface not accessible'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def generate_setup_instructions(config: Dict, authentik_config: Dict) -> str:
    """Generate account setup instructions for family members."""
    
    authentik_url = authentik_config.get('url')
    domain = config.get('domain', 'family.local')
    family_accounts = create_family_accounts(config, authentik_config)
    
    instructions = f"""
# Authentik SSO Setup Instructions

## Initial Admin Setup

### 1. Access Authentik
1. Open browser: {authentik_url}
2. You'll see the initial setup screen
3. Create admin account:
   - Username: admin
   - Email: admin@{domain}
   - Password: [Choose a strong password]

### 2. Configure Basic Settings
1. Go to: Settings → System
2. Set "External domain" to: https://{domain}
3. Configure email settings for password resets

### 3. Create Family Groups
1. Go to: Directory → Groups
2. Create groups:
   - "Parents" (superuser access)
   - "Children" (restricted access)
   - "Family" (all family members)

## Family Account Setup

### Parent Accounts
Create admin accounts for parents:

#### Parent 1:
- Username: parent1
- Email: parent1@{domain}
- Password: {family_accounts['parents'][0]['password']}
- Groups: Parents, Family
- MFA: Enable authenticator app

#### Parent 2:
- Username: parent2  
- Email: parent2@{domain}
- Password: {family_accounts['parents'][1]['password']}
- Groups: Parents, Family
- MFA: Enable authenticator app

### Child Accounts
Create restricted accounts for children:
"""
    
    for i, child in enumerate(family_accounts['children']):
        instructions += f"""
#### Child {i+1}:
- Username: {child['username']}
- Email: {child['email']}
- Password: {child['password']}
- Groups: Children, Family
- Restrictions: Enable content filtering
"""
    
    instructions += f"""
## Application Integration

### Nextcloud Integration
1. Go to: Applications → Providers
2. Create "OAuth2/OpenID Provider"
3. Name: Nextcloud
4. Client ID: nextcloud-oidc
5. Client Secret: {configure_oidc(config, authentik_config)['client_secret']}
6. Redirect URIs:
   - http://nextcloud.{domain}/apps/oidclogin/oidc/
   - http://nextcloud.{domain}/login

### Other Services
Configure SSO for other family services:
- Home Assistant (if used)
- Media servers (Plex, Jellyfin)
- Document management
- Calendar services

## Security Configuration

### Multi-Factor Authentication
1. Enable MFA for all parent accounts
2. Use authenticator apps (Google Authenticator, Authy)
3. Print backup codes and store safely

### Password Policies
1. Minimum password length: 12 characters
2. Require password changes every 90 days
3. Enable password strength indicators

### Access Controls
1. Set up device restrictions for children
2. Configure time-based access limits
3. Enable session timeout after inactivity

## User Management

### Daily Administration
1. Monitor user activity logs
2. Review failed login attempts
3. Update group memberships as needed

### Account Recovery
1. Set up password reset email
2. Configure security questions
3. Print emergency access codes

## Troubleshooting

### If users can't login:
- Check account is active
- Verify group memberships
- Reset password if needed
- Check MFA device sync

### If SSO isn't working:
- Verify provider configuration
- Check redirect URIs match
- Review application logs
- Test with incognito browser

### If MFA fails:
- Use backup codes
- Reset MFA device
- Verify time sync on device

## Ongoing Maintenance

### Monthly Tasks:
- Review user access logs
- Update security settings
- Test backup codes
- Check for software updates

### Quarterly Tasks:
- Audit user accounts
- Update group policies
- Review security settings
- Test disaster recovery

## Emergency Procedures

### Account Compromise:
1. Immediately disable affected account
2. Reset password and MFA
3. Review access logs
4. Notify other family members

### System Outage:
1. Check container status
2. Review system logs
3. Restart services if needed
4. Communicate with family

Keep this document secure and share only with trusted family members.
"""
    
    return instructions

def generate_random_password(length: int = 12) -> str:
    """Generate a random password."""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

if __name__ == '__main__':
    # Test the module
    test_config = {
        'homelab_ip': '192.168.1.100',
        'family_size': 4,
        'domain': 'family.local',
        'authentik_web_port': 9000
    }
    
    result = deploy_authentik(test_config)
    print(json.dumps(result, indent=2))
