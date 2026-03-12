#!/usr/bin/env python3
"""
Shut The Front Door! - Installer Entry Point
Stage 2: Guided Deployment Application

This is the main entry point that users run to start the installer.
It launches a local web server and opens the browser automatically.
"""

import sys
import os
import webbrowser
import time
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from server import create_app

def main():
    """Main entry point for the installer."""
    print("🚪 Shut The Front Door! - Installer")
    print("=" * 50)
    print("Starting local web server...")
    
    # Create Flask app
    app = create_app()
    
    # Find an available port (try 3000 first, then alternatives)
    port = 3000
    while True:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            break
        except OSError:
            port += 1
            if port > 3010:
                print("❌ Could not find an available port")
                return 1
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(1.5)
        try:
            webbrowser.open(f'http://localhost:{port}')
            print(f"🌐 Browser opened: http://localhost:{port}")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print(f"🔗 Please open manually: http://localhost:{port}")
    
    import threading
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    print(f"🚀 Server starting on http://localhost:{port}")
    print("📝 Press Ctrl+C to stop the installer")
    print("=" * 50)
    
    try:
        # Run the Flask app
        app.run(host='localhost', port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 Installer stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
