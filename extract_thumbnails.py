"""
NetworkBuster Network Map Thumbnail Extractor
Generates static thumbnail images from network topology
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

def extract_network_thumbnails():
    """Extract and save network device thumbnails"""
    
    # Create thumbnails directory
    thumb_dir = Path('network_thumbnails')
    thumb_dir.mkdir(exist_ok=True)
    
    print("📸 Network Map Thumbnail Extractor")
    print("="*60)
    
    # Device configurations for thumbnail generation
    devices = {
        'workstation': {
            'icon': '🖥️',
            'name': 'Primary Workstation',
            'type': 'Hardware',
            'status': 'online'
        },
        'router-wifi7': {
            'icon': '🌐',
            'name': 'WiFi 7 Mesh Router',
            'type': 'Network',
            'status': 'online'
        },
        'router-networkbuster': {
            'icon': '🔧',
            'name': 'NetworkBuster Router',
            'type': 'Network',
            'status': 'online'
        },
        'mesh-node-1': {
            'icon': '📡',
            'name': 'Mesh Node Alpha',
            'type': 'Network',
            'status': 'online'
        },
        'mesh-node-2': {
            'icon': '📡',
            'name': 'Mesh Node Beta',
            'type': 'Network',
            'status': 'online'
        },
        'mesh-node-3': {
            'icon': '📡',
            'name': 'Mesh Node Gamma',
            'type': 'Network',
            'status': 'online'
        },
        'service-web': {
            'icon': '⚡',
            'name': 'Web Server (3000)',
            'type': 'Service',
            'status': 'running'
        },
        'service-api': {
            'icon': '⚡',
            'name': 'API Server (3001)',
            'type': 'Service',
            'status': 'running'
        },
        'service-audio': {
            'icon': '⚡',
            'name': 'Audio Stream (3002)',
            'type': 'Service',
            'status': 'running'
        },
        'service-mission': {
            'icon': '⚡',
            'name': 'Mission Control (5000)',
            'type': 'Service',
            'status': 'running'
        }
    }
    
    # Generate HTML thumbnail for each device
    extracted = 0
    for device_id, info in devices.items():
        thumb_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{info['name']} - Thumbnail</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            font-family: 'Segoe UI', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .thumbnail {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            min-width: 300px;
            border: 3px solid {'#4CAF50' if info['status'] in ['online', 'running'] else '#f44336'};
        }}
        .device-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #eee;
        }}
        .device-icon {{
            font-size: 48px;
        }}
        .device-info h1 {{
            font-size: 24px;
            margin: 0 0 5px 0;
            color: #333;
        }}
        .device-info p {{
            font-size: 14px;
            color: #666;
            margin: 0;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            background: {'#4CAF50' if info['status'] in ['online', 'running'] else '#f44336'};
            color: white;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 10px;
        }}
        .metadata {{
            margin-top: 20px;
            padding-top: 15px;
            border-top: 2px solid #eee;
            font-size: 12px;
            color: #666;
        }}
        .metadata div {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="thumbnail">
        <div class="device-header">
            <div class="device-icon">{info['icon']}</div>
            <div class="device-info">
                <h1>{info['name']}</h1>
                <p>{info['type']}</p>
            </div>
        </div>
        <div class="status-badge">{info['status'].upper()}</div>
        <div class="metadata">
            <div><strong>Device ID:</strong> {device_id}</div>
            <div><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            <div><strong>NetworkBuster:</strong> v1.0.1</div>
        </div>
    </div>
</body>
</html>"""
        
        # Save thumbnail HTML
        thumb_path = thumb_dir / f"{device_id}.html"
        with open(thumb_path, 'w', encoding='utf-8') as f:
            f.write(thumb_html)
        
        extracted += 1
        print(f"   ✅ {info['name']}")
    
    # Create thumbnail index
    index_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NetworkBuster Thumbnail Gallery</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #0a0a0a;
            color: #00ff00;
            font-family: 'Courier New', monospace;
        }
        .header {
            text-align: center;
            padding: 30px;
            background: rgba(0, 255, 0, 0.1);
            border: 2px solid #00ff00;
            margin-bottom: 30px;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .thumb-link {
            display: block;
            padding: 20px;
            background: rgba(0, 255, 0, 0.05);
            border: 2px solid #00ff00;
            text-decoration: none;
            color: #00ff00;
            transition: all 0.3s;
        }
        .thumb-link:hover {
            background: rgba(0, 255, 0, 0.2);
            transform: scale(1.05);
        }
        .thumb-icon {
            font-size: 48px;
            text-align: center;
            margin-bottom: 10px;
        }
        .thumb-name {
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 NetworkBuster Thumbnail Gallery</h1>
        <p>Extracted Network Device Thumbnails</p>
        <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    </div>
    <div class="gallery">"""
    
    for device_id, info in devices.items():
        index_html += f"""
        <a href="{device_id}.html" class="thumb-link" target="_blank">
            <div class="thumb-icon">{info['icon']}</div>
            <div class="thumb-name">{info['name']}</div>
        </a>"""
    
    index_html += """
    </div>
</body>
</html>"""
    
    # Save index
    index_path = thumb_dir / 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    # Create metadata JSON
    metadata = {
        'generated': datetime.now().isoformat(),
        'version': '1.0.1',
        'total_devices': len(devices),
        'devices': devices
    }
    
    metadata_path = thumb_dir / 'thumbnails.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*60)
    print(f"✅ Extracted {extracted} thumbnails")
    print(f"📁 Location: {thumb_dir.absolute()}")
    print(f"🌐 Index: {index_path.absolute()}")
    print(f"📊 Metadata: {metadata_path.absolute()}")
    
    return thumb_dir, extracted

if __name__ == '__main__':
    extract_network_thumbnails()
