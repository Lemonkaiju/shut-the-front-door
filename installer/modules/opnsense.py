"""
Shut The Front Door! - OPNsense Deployment Module
Stage 2: Guided Deployment Application

Module 2: OPNsense firewall configuration
Imports pre-generated configuration and sets up network rules
"""

import json
from pathlib import Path
from typing import Dict, Any

def deploy_opnsense(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Configure OPNsense firewall with privacy network settings.
    
    Args:
        config: Installation configuration containing network details
        
    Returns:
        Dict with deployment status and details
    """
    print("🔒 Starting OPNsense configuration...")
    
    result = {
        'module': 'opnsense',
        'status': 'started',
        'steps': [],
        'config': {},
        'errors': []
    }
    
    try:
        # Step 1: Validate configuration
        result['steps'].append({
            'name': 'Validating OPNsense configuration',
            'status': 'running'
        })
        
        router_ip = config.get('router_ip')
        if not router_ip:
            raise ValueError("Router IP address is required")
        
        result['steps'][0]['status'] = 'completed'
        
        # Step 2: Generate OPNsense configuration
        result['steps'].append({
            'name': 'Generating OPNsense configuration',
            'status': 'running'
        })
        
        config_xml = generate_opnsense_config(config)
        result['config']['config_xml'] = config_xml
        
        result['steps'][1]['status'] = 'completed'
        
        # Step 3: Create configuration file
        result['steps'].append({
            'name': 'Creating configuration files',
            'status': 'running'
        })
        
        config_file = save_opnsense_config(config_xml, config)
        result['config']['config_file'] = config_file
        
        result['steps'][2]['status'] = 'completed'
        
        # Step 4: Generate setup instructions
        result['steps'].append({
            'name': 'Generating setup instructions',
            'status': 'running'
        })
        
        instructions = generate_setup_instructions(config)
        result['config']['instructions'] = instructions
        
        result['steps'][3]['status'] = 'completed'
        
        result['status'] = 'completed'
        print("✅ OPNsense configuration generated successfully!")
        
    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(str(e))
        print(f"❌ OPNsense configuration failed: {e}")
    
    return result

def generate_opnsense_config(config: Dict[str, Any]) -> str:
    """Generate OPNsense configuration XML."""
    
    router_ip = config.get('router_ip', '192.168.1.1')
    homelab_ip = config.get('homelab_ip', '192.168.1.100')
    wg_server_ip = config.get('vps_ip')
    
    config_template = f"""<?xml version="1.0"?>
<opnsense>
    <version>23.7</version>
    <system>
        <hostname>sovereign-gateway</hostname>
        <domain>local</domain>
        <dnsallowoverride>on</dnsallowoverride>
    </system>
    
    <aliases>
        <alias>
            <name>Streaming_AU</name>
            <type>network</type>
            <content>AS13335,AS38622,AS4773,AS38895</content>
            <descr>Australian Streaming CDNs and ASNs</descr>
        </alias>
        <alias>
            <name>Streaming_Global</name>
            <type>network</type>
            <content>AS2906,AS40027,AS16509,AS14618</content>
            <descr>Global Streaming Services (Netflix, Amazon, Disney+)</descr>
        </alias>
    </aliases>
    
    <interfaces>
        <wan>
            <enable>1</enable>
            <if>em0</if>
            <descr>WAN</descr>
        </wan>
        <lan>
            <enable>1</enable>
            <if>em1</if>
            <ipaddr>{router_ip}</ipaddr>
            <subnet>24</subnet>
            <descr>LAN</descr>
        </lan>
    </interfaces>
    
    <staticroutes>
        <!-- Route to WireGuard server -->
        <route>
            <network>{wg_server_ip}/32</network>
            <gateway>WAN_DHCP</gateway>
            <descr>Route to WireGuard server</descr>
        </route>
    </staticroutes>
    
    <gateways>
        <!-- WAN gateway will be auto-configured -->
    </gateways>
    
    <dnsmasq>
        <enable>1</enable>
        <regdhcpstatic>1</regdhcpstatic>
        <nohosts>0</nohosts>
        <customoptions>server=127.0.0.1#53</customoptions>
    </dnsmasq>
    
    <unbound>
        <enable>1</enable>
        <active_interface>lan</active_interface>
        <outgoing_interface>wan</outgoing_interface>
        <custom_options>forward-zone:
    name: "."
    forward-addr: 127.0.0.1@53
    forward-tls-upstream: no</custom_options>
    <dnssec>1</dnssec>
    <forwarding>1</forwarding>
    <regdhcpstatic>1</regdhcpstatic>
    <txtsupport>1</txtsupport>
    <private_domain>local</private_domain>
    <private_domain>lan</private_domain>
    <domain>local</domain>
    <domain>lan</domain>
    <domain>home</domain>
    <domain>internal</domain>
    <domain>corp</domain>
    <domain>private</domain>
    <domain>mail</domain>
    <domain>localdomain</domain>
    <domain>localhost</domain>
    <domain>localdomain</domain>
    <domain>example</domain>
        <domain>invalid</domain>
        <domain>test</domain>
        <domain>anchor</domain>
        <domain>broadcasthost</domain>
        <domain>ip6-localnet</domain>
        <domain>ip6-mcastprefix</domain>
        <domain>ip6-allnodes</domain>
        <domain>ip6-allrouters</domain>
        <domain>ip6-allhosts</domain>
        <domain>local</domain>
    </unbound>
    
    <nat>
        <outbound>
            <mode>hybrid</mode>
        </outbound>
        
        <!-- Port forward for AdGuard Home DNS -->
        <rule>
            <descr>AdGuard DNS</descr>
            <protocol>tcp/udp</protocol>
            <external-port>53</external-port>
            <target>{homelab_ip}</target>
            <local-port>53</local-port>
            <interface>lan</interface>
        </rule>
    </nat>
    
    <filter>
        <!-- Local Breakout AU Streaming (Always bypass VPN) -->
        <rule>
            <descr>Local Breakout AU Streaming</descr>
            <type>pass</type>
            <interface>lan</interface>
            <ipprotocol>inet</ipprotocol>
            <statetype>keep state</statetype>
            <source>
                <network>lan</network>
            </source>
            <destination>
                <network>Streaming_AU</network>
            </destination>
            <gateway>WAN_DHCP</gateway>
            <quick>1</quick>
        </rule>
        {f'''
        <!-- Global Streaming Breakout (User Toggle) -->
        <rule>
            <descr>Local Breakout Global Streaming</descr>
            <type>pass</type>
            <interface>lan</interface>
            <ipprotocol>inet</ipprotocol>
            <statetype>keep state</statetype>
            <source>
                <network>lan</network>
            </source>
            <destination>
                <network>Streaming_Global</network>
            </destination>
            <gateway>WAN_DHCP</gateway>
            <quick>1</quick>
        </rule>''' if config.get('bypass_global') else ''}
        
        <!-- Allow all LAN traffic -->
        <rule>
            <descr>Allow all LAN traffic</descr>
            <type>pass</type>
            <interface>lan</interface>
            <ipprotocol>inet</ipprotocol>
            <statetype>keep state</statetype>
            <source>
                <network>lan</network>
            </source>
            <destination>
                <any/>
            </destination>
        </rule>
        
        <!-- Allow established connections -->
        <rule>
            <descr>Allow established connections</descr>
            <type>pass</type>
            <interface>wan</interface>
            <ipprotocol>inet</ipprotocol>
            <statetype>keep state</statetype>
            <source>
                <any/>
            </source>
            <destination>
                <any/>
            </destination>
        </rule>
        
        <!-- Block all other WAN traffic -->
        <rule>
            <descr>Block all other WAN traffic</descr>
            <type>block</type>
            <interface>wan</interface>
            <ipprotocol>inet</ipprotocol>
            <statetype>keep state</statetype>
            <source>
                <any/>
            </source>
            <destination>
                <any/>
            </destination>
        </rule>
    </filter>
    
    <dhcpd>
        <lan>
            <enable>1</enable>
            <range>
                <from>{router_ip[:-1]}100</from>
                <to>{router_ip[:-1]}200</to>
            </range>
            <defaultleasetime>7200</defaultleasetime>
            <maxleasetime>86400</maxleasetime>
            <dnsserver>{router_ip}</dnsserver>
            <gateway>{router_ip}</gateway>
            <domain>local</domain>
            <ddnsdomain>local</ddnsdomain>
            <ddnsdomainprimary>127.0.0.1</ddnsdomainprimary>
            <ddnsdomainkeyname>none</ddnsdomainkeyname>
            <ddnsdomainkey>none</ddnsdomainkey>
            <mac_allow/>
            <mac_deny/>
        </lan>
    </dhcpd>
    
    <syslog>
        <enable>1</enable>
        <nentries>50</nentries>
        <sourceip>127.0.0.1</sourceip>
        <ipproto>ipv4</ipproto>
        <filter>default</filter>
        <descriptions>1</descriptions>
        <reverse>1</reverse>
        <nentries>50</nentries>
        <sourceip>127.0.0.1</sourceip>
        <ipproto>ipv4</ipproto>
        <filter>default</filter>
        <descriptions>1</descriptions>
        <reverse>1</reverse>
    </syslog>
</opnsense>
"""
    
    return config_template

def save_opnsense_config(config_xml: str, config: Dict[str, Any]) -> str:
    """Save OPNsense configuration to file."""
    
    config_dir = Path('generated_configs')
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / 'opnsense_config.xml'
    
    with open(config_file, 'w') as f:
        f.write(config_xml)
    
    return str(config_file)

def generate_setup_instructions(config: Dict[str, Any]) -> str:
    """Generate step-by-step setup instructions for OPNsense."""
    
    router_ip = config.get('router_ip', '192.168.1.1')
    config_file = 'generated_configs/opnsense_config.xml'
    
    instructions = f"""
# OPNsense Setup Instructions

## Prerequisites
- OPNsense installed on your edge hardware
- Physical access to the router
- Network cable from router to your main switch

## Setup Steps

### 1. Access OPNsense Web Interface
1. Connect computer to router LAN port
2. Open browser: https://{router_ip}
3. Default credentials: admin / opnsense

### 2. Import Configuration
1. Navigate to: System → Backup → Restore
2. Choose "Restore configuration"
3. Upload the configuration file: {config_file}
4. Click "Restore" and wait for reboot

### 3. Verify Network Settings
1. After reboot, login again
2. Check: Interfaces → Assignments
3. Verify LAN interface is configured with IP {router_ip}

### 4. Test DNS Resolution
1. Connect a device to the network
2. Try to resolve a domain: `nslookup google.com`
3. Should resolve through AdGuard Home (if deployed)

### 5. Verify Firewall Rules
1. Navigate to: Firewall → Rules → LAN
2. Verify "Allow all LAN traffic" rule exists
3. Navigate to: Firewall → Rules → WAN
4. Verify proper blocking rules are in place

### 6. Configure DHCP (if needed)
1. Navigate to: Services → DHCP Server → LAN
2. Verify range: {router_ip[:-1]}100 - {router_ip[:-1]}200
3. Verify DNS server is set to {router_ip}

### 7. Test Internet Connectivity
1. Connect device to network
2. Browse to https://dnsleaktest.com
3. Verify DNS is being filtered
4. Verify IP is masked (if WireGuard is active)

## Troubleshooting

### If devices can't get IP addresses:
- Check DHCP server status in Services → DHCP Server
- Verify LAN interface is up and configured correctly

### If DNS resolution fails:
- Check if AdGuard Home is deployed and running
- Verify DNS forwarding rules in Unbound

### If internet doesn't work:
- Check WAN interface has connection
- Verify firewall rules aren't blocking traffic
- Check NAT rules are properly configured

## Advanced Configuration

After basic setup, you may want to:
- Configure VLANs for network segmentation
- Set up port forwarding for specific services
- Configure traffic shaping
- Set up VPN client configurations

## Security Recommendations

1. Change default admin password
2. Enable two-factor authentication
3. Configure proper logging
4. Set up alerts for suspicious activity
5. Regularly backup configuration
"""
    
    return instructions

if __name__ == '__main__':
    # Test the module
    test_config = {
        'router_ip': '192.168.1.1',
        'homelab_ip': '192.168.1.100',
        'vps_ip': '123.45.67.89'
    }
    
    result = deploy_opnsense(test_config)
    print(json.dumps(result, indent=2))
