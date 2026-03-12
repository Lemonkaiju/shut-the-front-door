"""
Shut The Front Door! - ISO Provisioning Module
Stage 2: Guided Deployment Application

Handles downloading OS ISOs and flashing them to USB drives via Rufus.
"""

import os
import sys
import json
import threading
import subprocess
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional

# ---------------------------------------------------------------------------
# ISO definitions
# ---------------------------------------------------------------------------

ISO_DEFINITIONS = {
    # ── Beginner ─────────────────────────────────────────────────────────────
    'lemonkaiju': {
        'id': 'lemonkaiju',
        'name': 'LemonKaijuOS (Bazzite)',
        'tagline': 'Privacy-ready family OS. Just works.',
        'description': 'Fedora-based immutable desktop. Mullvad Browser, gaming drivers, and automatic updates pre-configured. Recommended for most families.',
        'role': 'Family Endpoint',
        'tier': 'beginner',
        'tier_label': 'Beginner',
        'url': 'https://download.bazzite.gg/bazzite-stable-x86_64.iso',
        'size_gb': 3.8,
        'sha256_url': 'https://download.bazzite.gg/bazzite-stable-x86_64.iso.sha256sum',
        'recommended': True,
    },
    'linuxmint': {
        'id': 'linuxmint',
        'name': 'Linux Mint 22 Cinnamon',
        'tagline': 'Feels like Windows. Great for older PCs.',
        'description': 'The friendliest Linux for Windows refugees. Traditional desktop layout, huge software library, runs well on decade-old hardware.',
        'role': 'Alternative Endpoint',
        'tier': 'beginner',
        'tier_label': 'Beginner',
        'url': 'https://mirrors.edge.kernel.org/linuxmint/stable/22/linuxmint-22-cinnamon-64bit.iso',
        'size_gb': 2.7,
        'sha256_url': 'https://mirrors.edge.kernel.org/linuxmint/stable/22/sha256sum.txt',
        'recommended': False,
    },

    # ── Workstation / Super Stable ────────────────────────────────────────────
    'debian': {
        'id': 'debian',
        'name': 'Debian 12 "Bookworm"',
        'tagline': 'Set it up once. Never fight updates again.',
        'description': 'The gold standard for stability. Packages only update for security fixes. Used in hospitals, banks, and NASA. If you need a machine that just works without drama, this is it.',
        'role': 'Workstation / Stable Desktop',
        'tier': 'workstation',
        'tier_label': 'Rock Solid',
        'url': 'https://cdimage.debian.org/debian-cd/current/amd64/iso-dvd/debian-12.10.0-amd64-DVD-1.iso',
        'size_gb': 3.9,
        'sha256_url': 'https://cdimage.debian.org/debian-cd/current/amd64/iso-dvd/SHA256SUMS',
        'recommended': False,
    },

    # ── Advanced / Techy ──────────────────────────────────────────────────────
    'cachyos': {
        'id': 'cachyos',
        'name': 'CachyOS',
        'tagline': 'Arch, but fast and actually installable.',
        'description': 'Arch-based with a performance-tuned kernel (BORE scheduler), one-click installer, and sensible defaults. All the power of Arch without the weekend-long setup.',
        'role': 'Power User Endpoint',
        'tier': 'advanced',
        'tier_label': 'Advanced',
        'url': 'https://mirror.cachyos.org/ISO/desktop/cachyos-desktop-linux-2502.iso',
        'size_gb': 2.8,
        'sha256_url': None,
        'recommended': False,
    },
    'arch': {
        'id': 'arch',
        'name': 'Arch Linux',
        'tagline': 'Total control. RTFM required.',
        'description': 'Minimal base system — you build exactly what you want and nothing more. Rolling release means always bleeding-edge. The wiki is legendary. Not for the faint-hearted, but deeply rewarding.',
        'role': 'Expert Endpoint',
        'tier': 'advanced',
        'tier_label': 'Expert',
        'url': 'https://mirrors.kernel.org/archlinux/iso/latest/archlinux-x86_64.iso',
        'size_gb': 1.2,
        'sha256_url': 'https://mirrors.kernel.org/archlinux/iso/latest/sha256sums.txt',
        'recommended': False,
    },

    # ── Infrastructure ────────────────────────────────────────────────────────
    'opnsense': {
        'id': 'opnsense',
        'name': 'OPNsense 24.7',
        'tagline': 'The Gatekeeper firewall OS.',
        'description': 'Open-source firewall and router platform. Powers the local breakout rules, DNS hijacking, and VPN routing in this privacy stack.',
        'role': 'Edge Firewall',
        'tier': 'infra',
        'tier_label': 'Infrastructure',
        'url': 'https://mirror.ams1.nl.leaseweb.net/opnsense/releases/24.7/OPNsense-24.7-dvd-amd64.iso.bz2',
        'size_gb': 1.1,
        'sha256_url': None,
        'recommended': False,
    },
    'ubuntu': {
        'id': 'ubuntu',
        'name': 'Ubuntu Server 24.04 LTS',
        'tagline': 'Homelab server for Docker services.',
        'description': 'The most popular Linux server OS. Runs AdGuard Home, Authentik, Nextcloud, and WireGuard via Docker Compose. Five years of security updates guaranteed.',
        'role': 'Homelab Server',
        'tier': 'infra',
        'tier_label': 'Infrastructure',
        'url': 'https://releases.ubuntu.com/24.04/ubuntu-24.04-live-server-amd64.iso',
        'size_gb': 2.6,
        'sha256_url': 'https://releases.ubuntu.com/24.04/SHA256SUMS',
        'recommended': False,
    },
}

# Rufus portable download URL (latest stable)
RUFUS_URL = 'https://github.com/pbatard/rufus/releases/download/v4.5/rufus-4.5p.exe'
RUFUS_FILENAME = 'rufus-portable.exe'

# ---------------------------------------------------------------------------
# Download state (in-process, shared with server)
# ---------------------------------------------------------------------------

_download_state: Dict[str, Any] = {}
_download_lock = threading.Lock()


def get_download_state(iso_id: str) -> Dict[str, Any]:
    with _download_lock:
        return dict(_download_state.get(iso_id, {'status': 'idle', 'progress': 0}))


def get_all_download_states() -> Dict[str, Any]:
    with _download_lock:
        return {k: dict(v) for k, v in _download_state.items()}


def _set_state(iso_id: str, **kwargs):
    with _download_lock:
        if iso_id not in _download_state:
            _download_state[iso_id] = {}
        _download_state[iso_id].update(kwargs)


# ---------------------------------------------------------------------------
# Download logic
# ---------------------------------------------------------------------------

def _download_worker(iso_id: str, dest_dir: Path):
    """Background thread: download ISO with progress tracking."""
    if iso_id not in ISO_DEFINITIONS:
        _set_state(iso_id, status='error', error=f'Unknown ISO: {iso_id}')
        return

    iso = ISO_DEFINITIONS[iso_id]
    url = iso['url']
    filename = url.split('/')[-1]
    dest_path = dest_dir / filename

    _set_state(iso_id, status='downloading', progress=0, filename=filename,
               dest_path=str(dest_path), message='Starting download...')

    try:
        # HEAD request to get file size
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=15) as resp:
            total = int(resp.headers.get('Content-Length', 0))

        downloaded = 0
        chunk_size = 1024 * 1024  # 1 MB

        with urllib.request.urlopen(url, timeout=60) as response, \
                open(dest_path, 'wb') as out_file:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                progress = int((downloaded / total) * 100) if total else 0
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                _set_state(
                    iso_id,
                    status='downloading',
                    progress=progress,
                    downloaded_mb=round(downloaded_mb, 1),
                    total_mb=round(total_mb, 1),
                    message=f'Downloading... {downloaded_mb:.0f} MB / {total_mb:.0f} MB'
                )

        _set_state(iso_id, status='complete', progress=100,
                   message='Download complete', dest_path=str(dest_path))

    except Exception as exc:
        _set_state(iso_id, status='error', error=str(exc),
                   message=f'Download failed: {exc}')


def download_iso(iso_id: str, dest_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Start an async ISO download. Returns immediately.
    Poll get_download_state(iso_id) for progress.
    """
    if iso_id not in ISO_DEFINITIONS:
        return {'success': False, 'error': f'Unknown ISO id: {iso_id}'}

    current = get_download_state(iso_id)
    if current.get('status') == 'downloading':
        return {'success': False, 'error': 'Already downloading'}

    if dest_dir is None:
        dest_dir = Path.home() / 'Downloads' / 'STFD-ISOs'
    dest_dir.mkdir(parents=True, exist_ok=True)

    t = threading.Thread(
        target=_download_worker,
        args=(iso_id, dest_dir),
        daemon=True
    )
    t.start()
    return {'success': True, 'message': f'Download started for {iso_id}'}


# ---------------------------------------------------------------------------
# USB drive detection (Windows via wmi, Linux via /proc/partitions)
# ---------------------------------------------------------------------------

def list_removable_drives() -> List[Dict[str, Any]]:
    """Return a list of removable drives safe to flash to."""
    drives = []

    if sys.platform == 'win32':
        drives = _list_drives_windows()
    else:
        drives = _list_drives_linux()

    return drives


def _list_drives_windows() -> List[Dict[str, Any]]:
    drives = []
    try:
        import wmi
        c = wmi.WMI()
        for disk in c.Win32_DiskDrive():
            if disk.MediaType and 'Removable' in str(disk.MediaType):
                size_gb = int(disk.Size or 0) / (1024 ** 3)
                # Get associated drive letters
                for partition in disk.associators('Win32_DiskDriveToDiskPartition'):
                    for logical in partition.associators('Win32_LogicalDiskToPartition'):
                        drives.append({
                            'letter': logical.DeviceID,
                            'label': logical.VolumeName or 'USB Drive',
                            'size_gb': round(size_gb, 1),
                            'model': disk.Model or 'Unknown',
                        })
    except ImportError:
        # wmi not installed - use subprocess fallback
        drives = _list_drives_windows_wmic()
    except Exception as exc:
        print(f'WMI drive detection error: {exc}')
    return drives


def _list_drives_windows_wmic() -> List[Dict[str, Any]]:
    """Fallback: use wmic command-line tool."""
    drives = []
    try:
        result = subprocess.run(
            ['wmic', 'logicaldisk', 'where', 'drivetype=2',
             'get', 'DeviceID,VolumeName,Size', '/format:csv'],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.splitlines():
            parts = line.strip().split(',')
            if len(parts) >= 4 and parts[1] and ':' in parts[1]:
                try:
                    size_gb = int(parts[3]) / (1024 ** 3) if parts[3].strip() else 0
                except ValueError:
                    size_gb = 0
                drives.append({
                    'letter': parts[1].strip(),
                    'label': parts[2].strip() or 'USB Drive',
                    'size_gb': round(size_gb, 1),
                    'model': 'Removable Drive',
                })
    except Exception as exc:
        print(f'wmic fallback error: {exc}')
    return drives


def _list_drives_linux() -> List[Dict[str, Any]]:
    """Detect removable drives on Linux via /sys/block."""
    drives = []
    try:
        for device in Path('/sys/block').iterdir():
            removable_path = device / 'removable'
            if removable_path.exists() and removable_path.read_text().strip() == '1':
                size_path = device / 'size'
                size_sectors = int(size_path.read_text().strip()) if size_path.exists() else 0
                size_gb = (size_sectors * 512) / (1024 ** 3)
                dev_name = device.name
                drives.append({
                    'letter': f'/dev/{dev_name}',
                    'label': f'USB Drive ({dev_name})',
                    'size_gb': round(size_gb, 1),
                    'model': 'Removable Drive',
                })
    except Exception as exc:
        print(f'Linux drive detection error: {exc}')
    return drives


# ---------------------------------------------------------------------------
# Rufus integration (Windows only)
# ---------------------------------------------------------------------------

def launch_rufus(iso_path: str, drive_letter: str,
                 rufus_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Download Rufus portable (if needed) and launch it pre-loaded with the ISO
    and target drive. Returns after launching - Rufus runs interactively.
    """
    if sys.platform != 'win32':
        return {'success': False, 'error': 'Rufus is Windows-only. Use dd on Linux.'}

    if rufus_dir is None:
        rufus_dir = Path.home() / 'Downloads' / 'STFD-ISOs'
    rufus_dir.mkdir(parents=True, exist_ok=True)

    rufus_path = rufus_dir / RUFUS_FILENAME

    # Download Rufus if not present
    if not rufus_path.exists():
        try:
            urllib.request.urlretrieve(RUFUS_URL, rufus_path)
        except Exception as exc:
            return {'success': False, 'error': f'Could not download Rufus: {exc}'}

    # Normalize drive letter (e.g. "E:" or "E:\")
    letter = drive_letter.rstrip('\\').rstrip('/')
    if not letter.endswith(':'):
        letter += ':'

    # Rufus CLI args: /iso:<path> /device:<letter> /start /close
    cmd = [
        str(rufus_path),
        f'/iso:{iso_path}',
        f'/device:{letter}',
    ]

    try:
        subprocess.Popen(cmd)
        return {
            'success': True,
            'message': f'Rufus launched with {Path(iso_path).name} → {letter}',
        }
    except Exception as exc:
        return {'success': False, 'error': f'Failed to launch Rufus: {exc}'}


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

def get_iso_list() -> List[Dict[str, Any]]:
    """Return ISO definitions enriched with current download state."""
    result = []
    for iso_id, iso in ISO_DEFINITIONS.items():
        entry = dict(iso)
        entry['download'] = get_download_state(iso_id)
        result.append(entry)
    return result
