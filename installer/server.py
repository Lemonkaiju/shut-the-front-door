"""
Shut The Front Door! - Web Server
Stage 2: Guided Deployment Application

Flask web server that provides the browser-based installer interface.
"""

import json
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                static_folder='web',
                template_folder='web',
                static_url_path='')
    
    # Enable CORS for local development
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-key-change-in-production'
    
    # State files
    CONFIG_FILE = Path('install_config.json')
    TRACKER_FILE = Path('../network_setup_tracker.md')
    LOG_FILE = Path('install_log.json')
    
    def load_config():
        """Load installation configuration."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save_config(config):
        """Save installation configuration."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def log_action(action, details=None, status='started'):
        """Log an installation action."""
        log_entry = {
            'timestamp': str(Path().cwd()),
            'action': action,
            'details': details or {},
            'status': status
        }
        
        logs = []
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, 'r') as f:
                    logs = json.load(f)
            except Exception:
                pass
        
        logs.append(log_entry)
        
        try:
            with open(LOG_FILE, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Error logging: {e}")
    
    # Routes
    @app.route('/')
    def index():
        """Main installer interface."""
        return render_template('index.html')
    
    @app.route('/api/config', methods=['GET', 'POST'])
    def api_config():
        """Get or update installation configuration."""
        if request.method == 'POST':
            config = request.json
            save_config(config)
            log_action('config_updated', config)
            return jsonify({'success': True})
        
        return jsonify(load_config())
    
    @app.route('/api/modules')
    def api_modules():
        """Get available deployment modules."""
        modules = [
            {
                'id': 'wireguard',
                'name': 'The Front Door',
                'description': 'WireGuard VPN on cloud VPS to hide your home IP',
                'status': 'pending',
                'required': ['vps_info', 'ssh_credentials']
            },
            {
                'id': 'opnsense',
                'name': 'The Gatekeeper', 
                'description': 'OPNsense firewall for network traffic control',
                'status': 'pending',
                'required': ['router_info', 'network_config']
            },
            {
                'id': 'adguard',
                'name': 'The Filter',
                'description': 'AdGuard Home DNS to block ads and trackers',
                'status': 'pending', 
                'required': ['homelab_info']
            },
            {
                'id': 'authentik',
                'name': 'Family Identity',
                'description': 'Authentik SSO for centralized family accounts',
                'status': 'pending',
                'required': ['family_info', 'domain_config']
            },
            {
                'id': 'nextcloud',
                'name': 'Private Cloud',
                'description': 'Nextcloud to replace Google Drive/Photos',
                'status': 'pending',
                'required': ['family_info', 'storage_config']
            },
            {
                'id': 'endpoints',
                'name': 'Device Setup',
                'description': 'Configure family devices with privacy tools',
                'status': 'pending',
                'required': ['device_list']
            }
        ]
        return jsonify(modules)
    
    @app.route('/api/deploy/<module_id>', methods=['POST'])
    def api_deploy_module(module_id):
        """Deploy a specific module."""
        config = load_config()
        
        # Import the module deployment function
        try:
            from modules import deploy_wireguard, deploy_opnsense, deploy_adguard
            from modules import deploy_authentik, deploy_nextcloud, deploy_endpoints
            
            deploy_functions = {
                'wireguard': deploy_wireguard,
                'opnsense': deploy_opnsense, 
                'adguard': deploy_adguard,
                'authentik': deploy_authentik,
                'nextcloud': deploy_nextcloud,
                'endpoints': deploy_endpoints
            }
            
            if module_id not in deploy_functions:
                return jsonify({'error': f'Unknown module: {module_id}'}), 400
            
            # Start deployment
            log_action(f'deploy_{module_id}_started', config)
            
            # This would run the actual deployment in a background thread
            # For now, return a placeholder response
            result = deploy_functions[module_id](config)
            
            log_action(f'deploy_{module_id}_completed', result)
            return jsonify(result)
            
        except ImportError as e:
            return jsonify({'error': f'Module not implemented: {e}'}), 501
        except Exception as e:
            log_action(f'deploy_{module_id}_error', {'error': str(e)})
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ai/chat', methods=['POST'])
    def api_ai_chat():
        """AI assistant chat interface."""
        message = request.json.get('message', '')
        config = load_config()
        
        try:
            from ai.assistant import get_ai_response
            response = get_ai_response(message, config)
            return jsonify({'response': response})
        except ImportError:
            # Fallback when AI module is not implemented
            fallback_responses = [
                "I'm still being configured. Please check the installation guide for help.",
                "The AI assistant is not yet available. Please proceed with the manual setup steps.",
                "I'm still learning! For now, please refer to the documentation."
            ]
            return jsonify({'response': fallback_responses[0]})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    @app.route('/api/ai/status')
    def api_ai_status():
        """Get AI provisioning status."""
        try:
            from ai.assistant import get_provisioning_status, detect_hardware_tier
            status = get_provisioning_status()
            # Also include hardware tier so UI knows what to expect
            if status['status'] == 'idle':
                hardware = detect_hardware_tier()
                status['hardware'] = hardware
            return jsonify(status)
        except ImportError:
            return jsonify({'status': 'error', 'error': 'AI module not found'})

    @app.route('/api/ai/provision', methods=['POST'])
    def api_ai_provision():
        """Start AI provisioning."""
        config = load_config()
        try:
            from ai.assistant import start_provisioning
            start_provisioning(config)
            return jsonify({'success': True})
        except ImportError:
            return jsonify({'error': 'AI module not found'}), 501
    
    # -----------------------------------------------------------------------
    # ISO download & USB flash endpoints
    # -----------------------------------------------------------------------

    @app.route('/api/isos/available')
    def api_isos_available():
        """Return list of supported ISOs with current download state."""
        try:
            from modules.isos import get_iso_list
            return jsonify(get_iso_list())
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/isos/download', methods=['POST'])
    def api_isos_download():
        """Start an async ISO download."""
        iso_id = request.json.get('iso_id')
        if not iso_id:
            return jsonify({'error': 'iso_id required'}), 400
        try:
            from modules.isos import download_iso
            result = download_iso(iso_id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/isos/status')
    def api_isos_status():
        """Poll progress for all or a specific ISO download."""
        iso_id = request.args.get('iso_id')
        try:
            from modules.isos import get_download_state, get_all_download_states
            if iso_id:
                return jsonify(get_download_state(iso_id))
            return jsonify(get_all_download_states())
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/usb/drives')
    def api_usb_drives():
        """List connected removable drives."""
        try:
            from modules.isos import list_removable_drives
            drives = list_removable_drives()
            return jsonify({'drives': drives})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/usb/flash', methods=['POST'])
    def api_usb_flash():
        """Launch Rufus (Windows) with the selected ISO and drive."""
        data = request.json or {}
        iso_id = data.get('iso_id')
        drive_letter = data.get('drive_letter')
        if not iso_id or not drive_letter:
            return jsonify({'error': 'iso_id and drive_letter required'}), 400
        try:
            from modules.isos import get_download_state, launch_rufus
            state = get_download_state(iso_id)
            dest_path = state.get('dest_path')
            if not dest_path or state.get('status') != 'complete':
                return jsonify({'error': 'ISO not downloaded yet'}), 400
            result = launch_rufus(dest_path, drive_letter)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/status')
    def api_status():
        """Get current installation status."""
        config = load_config()
        
        # Check if tracker file exists and read it
        tracker_content = ""
        if TRACKER_FILE.exists():
            try:
                with open(TRACKER_FILE, 'r') as f:
                    tracker_content = f.read()
            except Exception:
                pass
        
        return jsonify({
            'config_exists': CONFIG_FILE.exists(),
            'tracker_exists': TRACKER_FILE.exists(),
            'tracker_content': tracker_content,
            'config': config
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=3000)
