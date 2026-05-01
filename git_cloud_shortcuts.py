"""
NetworkBuster - Git Repository Cloud Shortcuts Creator
Finds all git repositories and creates shortcuts for cloud access
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
import shutil

def find_git_repositories(root_path='.'):
    """Find all git repositories in the project"""
    git_repos = []
    root_path = Path(root_path).resolve()
    
    for item in root_path.rglob('.git'):
        if item.is_dir():
            repo_path = item.parent
            repo_info = get_repo_info(repo_path)
            if repo_info:
                git_repos.append(repo_info)
    
    return git_repos

def get_repo_info(repo_path):
    """Get detailed information about a git repository"""
    try:
        os.chdir(repo_path)
        
        # Get branch
        branch = subprocess.check_output(
            ['git', 'branch', '--show-current'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # Get remote URL
        try:
            remote_url = subprocess.check_output(
                ['git', 'config', '--get', 'remote.origin.url'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            remote_url = 'No remote configured'
        
        # Get last commit
        try:
            last_commit = subprocess.check_output(
                ['git', 'log', '-1', '--format=%h - %s (%cr)'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            last_commit = 'No commits'
        
        # Get status
        try:
            status = subprocess.check_output(
                ['git', 'status', '--short'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            modified_files = len(status.split('\n')) if status else 0
        except:
            modified_files = 0
        
        # Get commit count
        try:
            commit_count = subprocess.check_output(
                ['git', 'rev-list', '--count', 'HEAD'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            commit_count = '0'
        
        return {
            'name': repo_path.name,
            'path': str(repo_path),
            'branch': branch,
            'remote_url': remote_url,
            'last_commit': last_commit,
            'modified_files': modified_files,
            'commit_count': commit_count,
            'size': get_folder_size(repo_path)
        }
    except Exception as e:
        print(f"Error getting info for {repo_path}: {e}")
        return None

def get_folder_size(folder_path):
    """Get total size of folder in bytes"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    pass
    except:
        pass
    return total_size

def format_size(bytes):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def create_shortcuts_folder(base_path):
    """Create folder structure for git shortcuts"""
    shortcuts_path = Path(base_path) / 'NetworkBuster_Git_Shortcuts'
    shortcuts_path.mkdir(exist_ok=True)
    return shortcuts_path

def create_windows_shortcut(repo_info, shortcuts_path):
    """Create Windows .lnk shortcut file"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        shortcut_name = f"{repo_info['name']}.lnk"
        shortcut_path = shortcuts_path / shortcut_name
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = repo_info['path']
        shortcut.WorkingDirectory = repo_info['path']
        shortcut.IconLocation = "shell32.dll,4"  # Folder icon with git
        shortcut.Description = f"Git: {repo_info['branch']} | {repo_info['commit_count']} commits"
        shortcut.save()
        
        return True
    except ImportError:
        # If winshell not available, create batch file instead
        batch_file = shortcuts_path / f"{repo_info['name']}.bat"
        with open(batch_file, 'w') as f:
            f.write(f'@echo off\n')
            f.write(f'cd /d "{repo_info["path"]}"\n')
            f.write(f'start "" "%SystemRoot%\\explorer.exe" "{repo_info["path"]}"\n')
        return True
    except Exception as e:
        print(f"Error creating shortcut for {repo_info['name']}: {e}")
        return False

def create_html_dashboard(repos, output_path):
    """Create HTML dashboard with all git repositories"""
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetworkBuster Git Repositories</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 36px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 18px;
            opacity: 0.8;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }}
        
        .stat-card h3 {{
            font-size: 32px;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-card p {{
            color: #666;
            font-size: 14px;
        }}
        
        .repos-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }}
        
        .repo-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s, box-shadow 0.3s;
            border-left: 5px solid #4CAF50;
        }}
        
        .repo-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
        }}
        
        .repo-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .repo-icon {{
            font-size: 40px;
        }}
        
        .repo-info h3 {{
            font-size: 20px;
            color: #333;
            margin-bottom: 5px;
        }}
        
        .repo-info .branch {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        
        .repo-details {{
            margin: 15px 0;
        }}
        
        .detail-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 0;
            font-size: 14px;
            color: #555;
        }}
        
        .detail-item .icon {{
            width: 20px;
            text-align: center;
        }}
        
        .commit-info {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            font-size: 12px;
            font-family: 'Consolas', monospace;
            margin: 10px 0;
            color: #333;
        }}
        
        .modified-badge {{
            display: inline-block;
            background: #ff9800;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
        }}
        
        .modified-badge.clean {{
            background: #4CAF50;
        }}
        
        .actions {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }}
        
        .btn {{
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: transform 0.2s;
            text-decoration: none;
            text-align: center;
            display: block;
        }}
        
        .btn:hover {{
            transform: scale(1.05);
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .btn-secondary {{
            background: #e9ecef;
            color: #333;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗂️ NetworkBuster Git Repositories</h1>
            <p>Cloud-Synced Repository Dashboard</p>
            <p style="font-size: 14px; margin-top: 10px;">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{len(repos)}</h3>
                <p>📦 Total Repositories</p>
            </div>
            <div class="stat-card">
                <h3>{sum(int(r['commit_count']) for r in repos)}</h3>
                <p>📝 Total Commits</p>
            </div>
            <div class="stat-card">
                <h3>{sum(r['modified_files'] for r in repos)}</h3>
                <p>🔧 Modified Files</p>
            </div>
            <div class="stat-card">
                <h3>{format_size(sum(r['size'] for r in repos))}</h3>
                <p>💾 Total Size</p>
            </div>
        </div>
        
        <div class="repos-grid">
"""
    
    for repo in repos:
        status_class = "clean" if repo['modified_files'] == 0 else ""
        status_text = "Clean" if repo['modified_files'] == 0 else f"{repo['modified_files']} modified"
        
        html_content += f"""
            <div class="repo-card">
                <div class="repo-header">
                    <div class="repo-icon">📁</div>
                    <div class="repo-info">
                        <h3>{repo['name']}</h3>
                        <span class="branch">🌿 {repo['branch']}</span>
                    </div>
                </div>
                
                <div class="repo-details">
                    <div class="detail-item">
                        <span class="icon">📍</span>
                        <span>{repo['path']}</span>
                    </div>
                    <div class="detail-item">
                        <span class="icon">🔗</span>
                        <span style="word-break: break-all;">{repo['remote_url']}</span>
                    </div>
                    <div class="detail-item">
                        <span class="icon">📊</span>
                        <span>{repo['commit_count']} commits • {format_size(repo['size'])}</span>
                    </div>
                </div>
                
                <div class="commit-info">
                    {repo['last_commit']}
                </div>
                
                <div class="detail-item">
                    <span class="modified-badge {status_class}">
                        {status_text}
                    </span>
                </div>
                
                <div class="actions">
                    <a href="file:///{repo['path']}" class="btn btn-primary">
                        📂 Open Folder
                    </a>
                    <a href="#" onclick="copyPath('{repo['path'].replace(chr(92), chr(92)+chr(92))}')" class="btn btn-secondary">
                        📋 Copy Path
                    </a>
                </div>
            </div>
"""
    
    html_content += """
        </div>
        
        <div class="footer">
            <p>🚀 NetworkBuster Cloud Git Manager</p>
            <p style="font-size: 12px; margin-top: 10px;">Synced to D: and K: drives • Auto-updated</p>
        </div>
    </div>
    
    <script>
        function copyPath(path) {
            navigator.clipboard.writeText(path).then(() => {
                alert('Path copied to clipboard: ' + path);
            });
        }
    </script>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def create_json_manifest(repos, output_path):
    """Create JSON manifest of all repositories"""
    manifest = {
        'generated': datetime.now().isoformat(),
        'total_repos': len(repos),
        'total_commits': sum(int(r['commit_count']) for r in repos),
        'total_size': sum(r['size'] for r in repos),
        'repositories': repos
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

def sync_to_cloud_drives(source_folder, repos):
    """Sync shortcuts to cloud drives"""
    cloud_drives = []
    
    # Check D: drive
    if os.path.exists('D:\\'):
        cloud_drives.append('D:\\NetworkBuster_Git_Cloud')
    
    # Check K: drive
    if os.path.exists('K:\\'):
        cloud_drives.append('K:\\NetworkBuster_Git_Cloud')
    
    synced_locations = []
    
    for drive_path in cloud_drives:
        try:
            os.makedirs(drive_path, exist_ok=True)
            
            # Copy HTML dashboard
            html_source = source_folder / 'git_dashboard.html'
            if html_source.exists():
                shutil.copy2(html_source, os.path.join(drive_path, 'git_dashboard.html'))
            
            # Copy JSON manifest
            json_source = source_folder / 'git_manifest.json'
            if json_source.exists():
                shutil.copy2(json_source, os.path.join(drive_path, 'git_manifest.json'))
            
            # Copy all shortcuts
            for file in source_folder.glob('*.bat'):
                shutil.copy2(file, drive_path)
            
            synced_locations.append(drive_path)
            print(f"✅ Synced to: {drive_path}")
        except Exception as e:
            print(f"❌ Failed to sync to {drive_path}: {e}")
    
    return synced_locations

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║  NetworkBuster - Git Cloud Shortcuts Creator             ║
║  Find and organize all git repositories                   ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("🔍 Scanning for git repositories...")
    repos = find_git_repositories()
    
    print(f"\n📦 Found {len(repos)} git repositories:")
    for repo in repos:
        print(f"   • {repo['name']} ({repo['branch']}) - {repo['commit_count']} commits")
    
    print("\n🗂️  Creating shortcuts folder...")
    shortcuts_path = create_shortcuts_folder('.')
    
    print("📝 Creating shortcuts...")
    for repo in repos:
        create_windows_shortcut(repo, shortcuts_path)
    
    print("🌐 Creating HTML dashboard...")
    html_path = shortcuts_path / 'git_dashboard.html'
    create_html_dashboard(repos, html_path)
    
    print("📋 Creating JSON manifest...")
    json_path = shortcuts_path / 'git_manifest.json'
    create_json_manifest(repos, json_path)
    
    print("\n☁️  Syncing to cloud drives...")
    synced_locations = sync_to_cloud_drives(shortcuts_path, repos)
    
    print("\n✅ All operations completed!")
    print(f"\n📁 Local shortcuts: {shortcuts_path}")
    print(f"🌐 Dashboard: {html_path}")
    print(f"📋 Manifest: {json_path}")
    
    if synced_locations:
        print("\n☁️  Cloud locations:")
        for location in synced_locations:
            print(f"   • {location}")
    
    print(f"\n📊 Summary:")
    print(f"   • {len(repos)} repositories")
    print(f"   • {sum(int(r['commit_count']) for r in repos)} total commits")
    print(f"   • {format_size(sum(r['size'] for r in repos))} total size")
    print(f"   • {sum(r['modified_files'] for r in repos)} modified files")
    
    # Open dashboard
    try:
        import webbrowser
        webbrowser.open(str(html_path))
        print("\n🚀 Opening dashboard in browser...")
    except:
        pass

if __name__ == '__main__':
    main()
