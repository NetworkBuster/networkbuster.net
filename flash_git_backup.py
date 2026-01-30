"""
NetworkBuster - Git Repository Flash Backup
Fast backup of entire git repository to multiple drives
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import json

def get_git_info():
    """Get current git repository information"""
    try:
        branch = subprocess.check_output(
            ['git', 'branch', '--show-current'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        commit = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        return {
            'branch': branch,
            'commit': commit,
            'timestamp': datetime.now().isoformat()
        }
    except:
        return None

def get_repo_stats():
    """Get repository statistics"""
    stats = {
        'files': 0,
        'size': 0,
        'folders': 0
    }
    
    for root, dirs, files in os.walk('.'):
        # Skip .git and other hidden folders
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.venv']]
        
        stats['folders'] += len(dirs)
        stats['files'] += len(files)
        
        for file in files:
            try:
                filepath = os.path.join(root, file)
                stats['size'] += os.path.getsize(filepath)
            except:
                pass
    
    return stats

def format_size(bytes):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def flash_to_drive(source_path, drive_letter, backup_name):
    """Flash entire repository to drive"""
    dest_path = f"{drive_letter}:\\{backup_name}"
    
    print(f"\n📦 Flashing to {drive_letter}: drive...")
    print(f"   Source: {source_path}")
    print(f"   Destination: {dest_path}")
    
    try:
        # Remove old backup if exists
        if os.path.exists(dest_path):
            print(f"   🗑️  Removing old backup...")
            shutil.rmtree(dest_path)
        
        # Create new backup
        print(f"   📋 Copying files...")
        shutil.copytree(
            source_path,
            dest_path,
            ignore=shutil.ignore_patterns(
                '.git',
                'node_modules',
                '__pycache__',
                '*.pyc',
                '.venv',
                'venv',
                '.env',
                '*.log'
            )
        )
        
        # Copy .git folder separately (for full git functionality)
        git_source = os.path.join(source_path, '.git')
        git_dest = os.path.join(dest_path, '.git')
        
        if os.path.exists(git_source):
            print(f"   🔧 Copying git repository...")
            shutil.copytree(git_source, git_dest)
        
        # Create backup info file
        info_file = os.path.join(dest_path, 'BACKUP_INFO.json')
        backup_info = {
            'backup_date': datetime.now().isoformat(),
            'source_path': source_path,
            'git_info': get_git_info(),
            'stats': get_repo_stats()
        }
        
        with open(info_file, 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        # Get backup size
        backup_size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, dirnames, filenames in os.walk(dest_path)
            for filename in filenames
        )
        
        print(f"   ✅ Successfully flashed to {drive_letter}:")
        print(f"      Size: {format_size(backup_size)}")
        print(f"      Path: {dest_path}")
        
        return {
            'success': True,
            'drive': drive_letter,
            'path': dest_path,
            'size': backup_size
        }
        
    except Exception as e:
        print(f"   ❌ Error flashing to {drive_letter}: {e}")
        return {
            'success': False,
            'drive': drive_letter,
            'error': str(e)
        }

def verify_backup(backup_path):
    """Verify backup integrity"""
    try:
        # Check if git repository is valid
        git_dir = os.path.join(backup_path, '.git')
        if not os.path.exists(git_dir):
            return False, "Git folder missing"
        
        # Check if backup info exists
        info_file = os.path.join(backup_path, 'BACKUP_INFO.json')
        if not os.path.exists(info_file):
            return False, "Backup info missing"
        
        # Count files
        file_count = sum(1 for _, _, files in os.walk(backup_path) for _ in files)
        if file_count < 10:
            return False, "Too few files"
        
        return True, f"Verified: {file_count} files"
    except Exception as e:
        return False, str(e)

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║  NetworkBuster - Git Repository Flash Backup             ║
║  Fast backup to multiple drives                           ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Get current directory
    source_path = os.getcwd()
    repo_name = os.path.basename(source_path)
    
    print(f"📂 Repository: {repo_name}")
    print(f"📍 Location: {source_path}")
    
    # Get git info
    git_info = get_git_info()
    if git_info:
        print(f"🌿 Branch: {git_info['branch']}")
        print(f"📝 Commit: {git_info['commit']}")
    
    # Get stats
    print("\n📊 Analyzing repository...")
    stats = get_repo_stats()
    print(f"   Files: {stats['files']:,}")
    print(f"   Folders: {stats['folders']:,}")
    print(f"   Size: {format_size(stats['size'])}")
    
    # Create backup name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"NetworkBuster_Backup_{timestamp}"
    
    # Flash to available drives
    results = []
    
    # Check D: drive
    if os.path.exists('D:\\'):
        result = flash_to_drive(source_path, 'D', backup_name)
        results.append(result)
        
        if result['success']:
            is_valid, msg = verify_backup(result['path'])
            if is_valid:
                print(f"   ✅ Verification: {msg}")
            else:
                print(f"   ⚠️ Verification failed: {msg}")
    
    # Check K: drive
    if os.path.exists('K:\\'):
        result = flash_to_drive(source_path, 'K', backup_name)
        results.append(result)
        
        if result['success']:
            is_valid, msg = verify_backup(result['path'])
            if is_valid:
                print(f"   ✅ Verification: {msg}")
            else:
                print(f"   ⚠️ Verification failed: {msg}")
    
    # Summary
    print("\n" + "="*60)
    print("📋 BACKUP SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    if successful:
        print(f"\n✅ Successfully backed up to {len(successful)} drive(s):")
        total_size = 0
        for result in successful:
            print(f"   • {result['drive']}: - {format_size(result['size'])}")
            print(f"     Path: {result['path']}")
            total_size += result['size']
        
        print(f"\n💾 Total backup size: {format_size(total_size)}")
    
    if failed:
        print(f"\n❌ Failed backups ({len(failed)}):")
        for result in failed:
            print(f"   • {result['drive']}: - {result['error']}")
    
    print("\n🎉 Flash backup complete!")
    print(f"📦 Backup name: {backup_name}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
