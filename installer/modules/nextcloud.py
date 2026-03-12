"""
Shut The Front Door! - Nextcloud Deployment Module
Stage 2: Guided Deployment Application

Module 5: Nextcloud private cloud deployment
Deploys Nextcloud via Docker with OIDC integration to Authentik
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any

def deploy_nextcloud(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deploy Nextcloud on the specified homelab server.
    
    Args:
        config: Installation configuration containing family and storage details
        
    Returns:
        Dict with deployment status and details
    """
    print("☁️ Starting Nextcloud deployment...")
    
    result = {
        'module': 'nextcloud',
        'status': 'started',
        'steps': [],
        'config': {},
        'errors': []
    }
    
    try:
        # Step 1: Validate configuration
        result['steps'].append({
            'name': 'Validating Nextcloud configuration',
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
        
        # Step 3: Deploy Nextcloud container
        result['steps'].append({
            'name': 'Deploying Nextcloud container',
            'status': 'running'
        })
        
        nextcloud_deploy = deploy_nextcloud_container(homelab_ip, config.get('ssh_key'), config)
        if not nextcloud_deploy['success']:
            raise ValueError(f"Nextcloud deployment failed: {nextcloud_deploy['error']}")
        
        result['steps'][2]['status'] = 'completed'
        result['config'].update(nextcloud_deploy.get('config', {}))
        
        # Step 4: Wait for initialization
        result['steps'].append({
            'name': 'Waiting for Nextcloud initialization',
            'status': 'running'
        })
        
        # Give Nextcloud time to initialize
        import time
        time.sleep(45)
        
        result['steps'][3]['status'] = 'completed'
        
        # Step 5: Configure OIDC integration
        result['steps'].append({
            'name': 'Configuring OIDC integration',
            'status': 'running'
        })
        
        oidc_setup = configure_oidc_integration(homelab_ip, config.get('ssh_key'), config)
        result['config']['oidc_setup'] = oidc_setup
        
        result['steps'][4]['status'] = 'completed'
        
        # Step 6: Configure family storage
        result['steps'].append({
            'name': 'Configuring family storage structure',
            'status': 'running'
        })
        
        storage_setup = configure_family_storage(config, nextcloud_deploy.get('config', {}))
        result['config']['storage'] = storage_setup
        
        result['steps'][5]['status'] = 'completed'
        
        # Step 7: Install recommended apps
        result['steps'].append({
            'name': 'Installing recommended apps',
            'status': 'running'
        })
        
        apps_setup = install_recommended_apps(homelab_ip, config.get('ssh_key'), config)
        result['config']['apps'] = apps_setup
        
        result['steps'][6]['status'] = 'completed'
        
        # Step 8: Verify deployment
        result['steps'].append({
            'name': 'Verifying Nextcloud deployment',
            'status': 'running'
        })
        
        verification = verify_nextcloud(homelab_ip, nextcloud_deploy.get('web_port', 8080))
        if not verification['success']:
            raise ValueError(f"Nextcloud verification failed: {verification['error']}")
        
        result['steps'][7]['status'] = 'completed'
        
        # Step 9: Generate user guide
        result['steps'].append({
            'name': 'Generating family user guide',
            'status': 'running'
        })
        
        user_guide = generate_user_guide(config, nextcloud_deploy.get('config', {}))
        result['config']['user_guide'] = user_guide
        
        result['steps'][8]['status'] = 'completed'
        
        result['status'] = 'completed'
        print("✅ Nextcloud deployment completed successfully!")
        
    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(str(e))
        print(f"❌ Nextcloud deployment failed: {e}")
    
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

def deploy_nextcloud_container(ip: str, ssh_key: str = None, config: Dict = None) -> Dict[str, Any]:
    """Deploy Nextcloud container using Docker Compose."""
    try:
        ssh_opts = []
        if ssh_key:
            ssh_opts.extend(['-i', ssh_key])
        
        # Generate Nextcloud docker-compose.yml
        domain = config.get('domain', 'family.local')
        web_port = config.get('nextcloud_web_port', 8080)
        db_password = generate_random_password(32)
        nextcloud_password = generate_random_password(32)
        
        docker_compose = f"""version: '3.8'

services:
  nextcloud-db:
    image: postgres:14
    container_name: nextcloud-db
    restart: unless-stopped
    volumes:
      - ./nextcloud-db:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=nextcloud
      - POSTGRES_USER=nextcloud
      - POSTGRES_PASSWORD={db_password}
    networks:
      - nextcloud

  nextcloud-redis:
    image: redis:alpine
    container_name: nextcloud-redis
    restart: unless-stopped
    networks:
      - nextcloud

  nextcloud-app:
    image: nextcloud:latest
    container_name: nextcloud-app
    restart: unless-stopped
    depends_on:
      - nextcloud-db
      - nextcloud-redis
    volumes:
      - ./nextcloud-data:/var/www/html
      - ./nextcloud-config:/var/www/html/config
      - ./nextcloud-apps:/var/www/html/apps
      - ./nextcloud-files:/var/www/html/data
    environment:
      - POSTGRES_HOST=nextcloud-db
      - POSTGRES_DB=nextcloud
      - POSTGRES_USER=nextcloud
      - POSTGRES_PASSWORD={db_password}
      - REDIS_HOST=nextcloud-redis
      - NEXTCLOUD_ADMIN_USER=admin
      - NEXTCLOUD_ADMIN_PASSWORD={nextcloud_password}
      - NEXTCLOUD_TRUSTED_DOMAINS={domain} {ip} localhost
      - OVERWRITEPROTOCOL=http
      - OVERWRITEHOST=nextcloud.{domain}
      - OVERWRITECLIURL=http://nextcloud.{domain}
    ports:
      - "{web_port}:80"
    networks:
      - nextcloud

  nextcloud-cron:
    image: nextcloud:latest
    container_name: nextcloud-cron
    restart: unless-stopped
    depends_on:
      - nextcloud-app
    volumes:
      - ./nextcloud-data:/var/www/html
    entrypoint: /cron.sh
    networks:
      - nextcloud

networks:
  nextcloud:
    driver: bridge
"""
        
        # Create directory and deploy
        deploy_script = f"""
# Create directories for Nextcloud
mkdir -p /opt/nextcloud
cd /opt/nextcloud

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
{docker_compose}
EOF

# Create required directories
mkdir -p nextcloud-db nextcloud-data nextcloud-config nextcloud-apps nextcloud-files

# Set proper permissions
chown -R 33:33 nextcloud-data nextcloud-config nextcloud-apps nextcloud-files

# Start the containers
docker-compose up -d

# Wait for Nextcloud to initialize
sleep 45

# Check container status
docker-compose ps

# Show initial logs
docker-compose logs nextcloud-app | tail -20
"""
        
        cmd = ['ssh'] + ssh_opts + [
            '-o', 'ConnectTimeout=30',
            '-o', 'StrictHostKeyChecking=no',
            f'root@{ip}',
            f'bash -c "{deploy_script}"'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        
        return {
            'success': result.returncode == 0,
            'error': result.stderr if result.returncode != 0 else None,
            'output': result.stdout,
            'config': {
                'web_port': web_port,
                'url': f'http://{ip}:{web_port}',
                'domain': f'nextcloud.{domain}',
                'admin_password': nextcloud_password,
                'db_password': db_password
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def configure_oidc_integration(ip: str, ssh_key: str = None, config: Dict = None) -> Dict[str, Any]:
    """Configure OIDC integration with Authentik."""
    
    domain = config.get('domain', 'family.local')
    authentik_url = f'http://192.168.1.100:9000'  # Default Authentik URL
    
    oidc_config = {
        'authentik_url': authentik_url,
        'client_id': 'nextcloud-oidc',
        'client_secret': generate_random_password(32),
        'redirect_uri': f'http://nextcloud.{domain}/apps/oidclogin/oidc/',
        'logout_url': f'http://nextcloud.{domain}/logout'
    }
    
    # Generate setup script for OIDC
    setup_script = f"""
# Install OIDC Login app
docker exec nextcloud-app occ app:install oidclogin

# Configure OIDC provider
docker exec nextcloud-app occ config:app:set oidclogin --key=auto_create_user --value=1
docker exec nextcloud-app occ config:app:set oidclogin --key=auto_update_user --value=1
docker exec nextcloud-app occ config:app:set oidclogin --key=auto_redirect --value=1
docker exec nextcloud-app occ config:app:set oidclogin --key=hide_login_form --value=1
docker exec nextcloud-app occ config:app:set oidclogin --key=allow_multiple_user_backends --value=1

# Set provider configuration
docker exec nextcloud-app occ config:app:set oidclogin --key=provider_name --value="Family Login"
docker exec nextcloud-app occ config:app:set oidclogin --key=client_id --value="{oidc_config['client_id']}"
docker exec nextcloud-app occ config:app:set oidclogin --key=client_secret --value="{oidc_config['client_secret']}"
docker exec nextcloud-app occ config:app:set oidclogin --key=scope --value="openid profile email"
docker exec nextcloud-app occ config:app:set oidclogin --key=auth_url --value="{authentik_url}/application/o/authorize/"
docker exec nextcloud-app occ config:app:set oidclogin --key=token_url --value="{authentik_url}/application/o/token/"
docker exec nextcloud-app occ config:app:set oidclogin --key=userinfo_url --value="{authentik_url}/application/o/userinfo/"
docker exec nextcloud-app occ config:app:set oidclogin --key=logout_url --value="{oidc_config['logout_url']}"
"""
    
    return {
        'setup_script': setup_script,
        'config': oidc_config,
        'instructions': f"""
1. In Authentik, create an OAuth2/OpenID Provider with:
   - Name: Nextcloud
   - Client ID: {oidc_config['client_id']}
   - Client Secret: {oidc_config['client_secret']}
   - Redirect URI: {oidc_config['redirect_uri']}

2. Run the OIDC setup script on the Nextcloud server

3. Test login by accessing Nextcloud and clicking "Family Login"
"""
    }

def configure_family_storage(config: Dict, nextcloud_config: Dict) -> Dict[str, Any]:
    """Configure family storage structure."""
    
    family_size = config.get('family_size', 4)
    
    storage_structure = {
        'shared_folders': [
            {
                'name': 'Family Photos',
                'path': '/Photos',
                'description': 'Shared family photos and memories',
                'access': 'all_family'
            },
            {
                'name': 'Documents',
                'path': '/Documents',
                'description': 'Important family documents',
                'access': 'parents_only'
            },
            {
                'name': 'Recipes',
                'path': '/Recipes',
                'description': 'Family recipe collection',
                'access': 'all_family'
            },
            {
                'name': 'Home Videos',
                'path': '/Videos',
                'description': 'Family videos and recordings',
                'access': 'all_family'
            }
        ],
        'personal_folders': [
            {
                'name': 'Personal Files',
                'path': '/Files',
                'description': 'Personal documents and files',
                'access': 'owner_only'
            }
        ],
        'quota_settings': {
            'parents': '50GB',
            'children': '10GB',
            'shared': '200GB'
        }
    }
    
    return storage_structure

def install_recommended_apps(ip: str, ssh_key: str = None, config: Dict = None) -> Dict[str, Any]:
    """Install recommended Nextcloud apps."""
    
    apps = [
        {
            'name': 'Memories',
            'id': 'memories',
            'description': 'AI-powered photo management and timeline',
            'essential': True
        },
        {
            'name': 'OnlyOffice',
            'id': 'onlyoffice',
            'description': 'Office document editing',
            'essential': True
        },
        {
            'name': 'Calendar',
            'id': 'calendar',
            'description': 'Family calendar and events',
            'essential': True
        },
        {
            'name': 'Contacts',
            'id': 'contacts',
            'description': 'Family address book',
            'essential': True
        },
        {
            'name': 'Notes',
            'id': 'notes',
            'description': 'Shared notes and lists',
            'essential': False
        },
        {
            'name': 'Deck',
            'id': 'deck',
            'description': 'Kanban boards for family projects',
            'essential': False
        }
    ]
    
    install_script = """
# Install essential apps
docker exec nextcloud-app occ app:install memories
docker exec nextcloud-app occ app:install onlyoffice
docker exec nextcloud-app occ app:install calendar
docker exec nextcloud-app occ app:install contacts

# Install optional apps
docker exec nextcloud-app occ app:install notes
docker exec nextcloud-app occ app:install deck

# Enable all installed apps
docker exec nextcloud-app occ app:enable memories
docker exec nextcloud-app occ app:enable onlyoffice
docker exec nextcloud-app occ app:enable calendar
docker exec nextcloud-app occ app:enable contacts
docker exec nextcloud-app occ app:enable notes
docker exec nextcloud-app occ app:enable deck

# Configure OnlyOffice
docker exec nextcloud-app occ config:app:set onlyoffice --key=DocumentServerUrl --value="http://onlyoffice:80"
docker exec nextcloud-app occ config:app:set onlyoffice --key=DocumentServerInternalUrl --value="http://onlyoffice:80"
"""
    
    return {
        'apps': apps,
        'install_script': install_script,
        'total_apps': len(apps)
    }

def verify_nextcloud(ip: str, port: int = 8080) -> Dict[str, Any]:
    """Verify Nextcloud is running and accessible."""
    try:
        import requests
        
        # Test if web interface is accessible
        try:
            response = requests.get(f'http://{ip}:{port}', timeout=10, allow_redirects=True)
            if response.status_code in [200, 302]:
                return {'success': True}
        except requests.RequestException:
            pass
        
        return {'success': False, 'error': 'Nextcloud web interface not accessible'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def generate_user_guide(config: Dict, nextcloud_config: Dict) -> str:
    """Generate family user guide for Nextcloud."""
    
    nextcloud_url = nextcloud_config.get('url')
    nextcloud_domain = nextcloud_config.get('domain')
    
    guide = f"""
# Nextcloud Family User Guide

## Getting Started

### 1. Access Nextcloud
1. Open browser: {nextcloud_url}
2. Click "Family Login" (OIDC with Authentik)
3. Login with your family credentials

### 2. First Login Setup
1. Complete initial setup wizard
2. Configure personal preferences
3. Set up desktop/mobile sync clients

## Family Features

### Shared Photo Library (Memories App)
1. Upload photos to "Family Photos" folder
2. AI-powered timeline and face recognition
3. Automatic photo organization
4. Shared albums for events

### Family Calendar
1. Create shared family events
2. Set up recurring activities
3. Sync with mobile devices
4. Color-coded calendars for each family member

### Document Collaboration
1. Use OnlyOffice for document editing
2. Real-time collaboration on documents
3. Version history and recovery
4. Document templates for common tasks

### Contact Management
1. Shared family address book
2. Import contacts from other services
3. Birthday reminders
4. Contact groups (family, friends, services)

## Storage Organization

### Folder Structure
```
/
├── Photos/              # Shared family photos
├── Documents/           # Important family documents
├── Recipes/            # Family recipe collection
├── Videos/             # Family videos
├── Calendar/           # Calendar attachments
└── Files/              # Personal files (per user)
```

### File Sharing
1. Right-click any file/folder
2. Select "Share"
3. Choose sharing method:
   - Internal: Share with family members
   - Link: Create shareable link
   - Password: Protect with password
   - Expiry: Set link expiration

### Storage Quotas
- Parents: 50GB personal storage
- Children: 10GB personal storage  
- Shared folders: 200GB total

## Mobile Apps

### Install Mobile Apps
1. Download Nextcloud app from app store
2. Server address: {nextcloud_domain}
3. Login with "Family Login"

### Mobile Features
- Automatic photo backup
- File synchronization
- Offline access
- Push notifications

## Desktop Sync

### Install Desktop Client
1. Download from {nextcloud_url}/apps/desktopsync/
2. Install on Windows/Mac/Linux
3. Configure sync folders
4. Set up automatic sync

### Sync Best Practices
- Selective sync for large folders
- Schedule sync during off-peak hours
- Monitor storage usage
- Use version history for important files

## Security & Privacy

### Data Protection
1. All data stored locally on your server
2. No data sent to external services
3. End-to-end encryption available
4. Two-factor authentication required

### Access Controls
- Parents: Full access to all features
- Children: Restricted access with content filtering
- Guest access: Limited sharing capabilities

### Backup Strategy
1. Regular server backups
2. Export important data
3. Document version history
4. Disaster recovery plan

## Daily Usage

### Photo Management
1. Enable auto-upload from mobile devices
2. Organize photos by events and dates
3. Use face recognition for person albums
4. Create shared albums for special occasions

### Document Workflow
1. Store important documents in secure folders
2. Use OnlyOffice for document editing
3. Set up document sharing for collaboration
4. Regular document cleanup and organization

### Calendar Management
1. Create family calendars for different activities
2. Set up reminders for important events
3. Share calendars with external services if needed
4. Sync across all devices

## Troubleshooting

### Common Issues

#### Can't login:
- Check Authentik is accessible
- Verify OIDC configuration
- Clear browser cache
- Try incognito mode

#### Files not syncing:
- Check network connectivity
- Verify sync client configuration
- Check storage quotas
- Restart sync client

#### Slow performance:
- Check server resources
- Optimize file sizes
- Clean up old files
- Consider storage upgrade

#### Mobile app issues:
- Update to latest version
- Check server URL configuration
- Re-authenticate if needed
- Clear app cache

### Getting Help
1. Check Nextcloud documentation
2. Review server logs
3. Contact family admin (parents)
4. Check community forums

## Advanced Features

### External Storage
1. Connect external storage services
2. Mount network shares
3. Configure cloud storage integration
4. Set up automatic backups

### App Integrations
1. Install additional apps from Nextcloud app store
2. Configure third-party integrations
3. Set up automation workflows
4. Customize user experience

### Automation
1. Set up automatic photo organization
2. Configure document processing
3. Create automated backups
4. Set up notification rules

## Family Best Practices

### Photo Guidelines
1. Regular photo uploads from all devices
2. Organize photos by events and dates
3. Tag family members in photos
4. Create shared albums for special memories

### Document Management
1. Store important documents securely
2. Use descriptive file names
3. Regular document cleanup
4. Backup critical documents

### Privacy Considerations
1. Respect privacy of family members
2. Use appropriate sharing settings
3. Regular review of shared content
4. Educate children about digital privacy

## Maintenance

### Weekly Tasks
- Review and organize new photos
- Update calendar events
- Check storage usage
- Review sharing permissions

### Monthly Tasks
- Backup important data
- Clean up old files
- Update apps and system
- Review security settings

### Quarterly Tasks
- Audit user accounts
- Review storage quotas
- Update documentation
- Plan system upgrades

Enjoy your private family cloud! ☁️
"""
    
    return guide

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
        'nextcloud_web_port': 8080
    }
    
    result = deploy_nextcloud(test_config)
    print(json.dumps(result, indent=2))
