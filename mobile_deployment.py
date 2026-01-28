#!/usr/bin/env python3
"""
NetworkBuster Mobile Deployment Manager
Build and deploy to iOS, Android, and Progressive Web App (PWA)
"""

import subprocess
import sys
import os
import json
import platform
from pathlib import Path
from datetime import datetime

PROJECT_PATH = Path(__file__).parent.resolve()
IS_WINDOWS = platform.system() == "Windows"

# Mobile deployment configuration
MOBILE_CONFIG = {
    "ios": {
        "platform": "iOS",
        "framework": "Capacitor",
        "bundle_id": "net.networkbuster.app",
        "min_version": "14.0",
        "xcode_project": "ios/App/App.xcodeproj",
        "simulator": "iPhone 15 Pro",
        "status": "pending"
    },
    "android": {
        "platform": "Android",
        "framework": "Capacitor",
        "package_name": "net.networkbuster.app",
        "min_sdk": "26",
        "gradle_path": "android/app/build.gradle",
        "emulator": "Pixel_7_API_34",
        "status": "pending"
    },
    "pwa": {
        "platform": "Progressive Web App",
        "manifest": "public/manifest.json",
        "service_worker": "public/sw.js",
        "icons_path": "public/icons",
        "status": "configured"
    }
}

BUILD_CONFIGS = {
    "development": {
        "mode": "dev",
        "source_maps": True,
        "minify": False,
        "api_url": "http://localhost:3001"
    },
    "staging": {
        "mode": "staging",
        "source_maps": True,
        "minify": True,
        "api_url": "https://staging.networkbuster.net"
    },
    "production": {
        "mode": "prod",
        "source_maps": False,
        "minify": True,
        "api_url": "https://api.networkbuster.net"
    }
}


def run_cmd(cmd, capture=True, cwd=None):
    """Run shell command."""
    result = subprocess.run(
        cmd, shell=True, capture_output=capture, text=True,
        cwd=cwd or PROJECT_PATH
    )
    return result


def check_prerequisites():
    """Check required tools for mobile deployment."""
    prereqs = {
        "node": run_cmd("node --version").returncode == 0,
        "npm": run_cmd("npm --version").returncode == 0,
        "capacitor": run_cmd("npx cap --version").returncode == 0,
    }
    
    if platform.system() == "Darwin":  # macOS
        prereqs["xcode"] = run_cmd("xcodebuild -version").returncode == 0
        prereqs["cocoapods"] = run_cmd("pod --version").returncode == 0
    
    prereqs["android_studio"] = run_cmd("adb --version").returncode == 0
    
    return prereqs


class MobileDeployment:
    """Manage mobile deployments."""
    
    def __init__(self):
        self.config = MOBILE_CONFIG.copy()
        self.prereqs = check_prerequisites()
    
    def show_status(self):
        """Show mobile deployment status."""
        print("\n" + "=" * 70)
        print("  📱 MOBILE DEPLOYMENT STATUS")
        print("=" * 70)
        
        # Prerequisites
        print("\n  🔧 Prerequisites:")
        for tool, installed in self.prereqs.items():
            status = "✓" if installed else "✗"
            print(f"     {status} {tool}")
        
        print("\n" + "-" * 70)
        
        # Platforms
        for platform_key, config in self.config.items():
            status_icon = "🟢" if config["status"] == "configured" else "🟡"
            print(f"\n  {status_icon} {config['platform']}")
            print(f"     Framework: {config.get('framework', 'Native')}")
            
            if platform_key == "ios":
                print(f"     Bundle ID: {config['bundle_id']}")
                print(f"     Min iOS: {config['min_version']}")
            elif platform_key == "android":
                print(f"     Package: {config['package_name']}")
                print(f"     Min SDK: {config['min_sdk']}")
            elif platform_key == "pwa":
                print(f"     Manifest: {config['manifest']}")
        
        print("\n" + "=" * 70)
    
    def setup_capacitor(self):
        """Initialize Capacitor for mobile."""
        print("\n⚡ Setting up Capacitor...")
        
        if not self.prereqs["npm"]:
            print("✗ npm not found")
            return False
        
        # Install Capacitor
        print("  Installing Capacitor...")
        run_cmd("npm install @capacitor/core @capacitor/cli", capture=False)
        
        # Initialize Capacitor
        print("  Initializing Capacitor...")
        run_cmd('npx cap init "NetworkBuster" "net.networkbuster.app"', capture=False)
        
        # Add platforms
        print("  Adding iOS platform...")
        run_cmd("npx cap add ios", capture=False)
        
        print("  Adding Android platform...")
        run_cmd("npx cap add android", capture=False)
        
        print("✓ Capacitor setup complete")
        return True
    
    def build_web(self, env="production"):
        """Build web assets."""
        print(f"\n🔨 Building web assets ({env})...")
        
        build_config = BUILD_CONFIGS.get(env, BUILD_CONFIGS["production"])
        
        # Set environment variables
        env_vars = {
            "NODE_ENV": build_config["mode"],
            "REACT_APP_API_URL": build_config["api_url"]
        }
        
        env_str = " ".join([f"{k}={v}" for k, v in env_vars.items()])
        
        # Build
        result = run_cmd(f"{env_str} npm run build", capture=False)
        
        if result.returncode == 0:
            print("✓ Web build complete")
            return True
        else:
            print("✗ Build failed")
            return False
    
    def sync_capacitor(self):
        """Sync web assets to mobile platforms."""
        print("\n🔄 Syncing assets to mobile platforms...")
        
        result = run_cmd("npx cap sync", capture=False)
        
        if result.returncode == 0:
            print("✓ Sync complete")
            return True
        else:
            print("✗ Sync failed")
            return False
    
    def build_ios(self, scheme="App"):
        """Build iOS app."""
        print(f"\n🍎 Building iOS app ({scheme})...")
        
        if platform.system() != "Darwin":
            print("✗ iOS builds require macOS")
            return False
        
        if not self.prereqs.get("xcode"):
            print("✗ Xcode not found")
            return False
        
        # Open in Xcode
        ios_project = PROJECT_PATH / "ios" / "App" / "App.xcworkspace"
        if ios_project.exists():
            print(f"  Opening {ios_project}")
            run_cmd(f'open "{ios_project}"', capture=False)
            print("  Build in Xcode: Product → Build")
        else:
            print("✗ iOS project not found. Run setup_capacitor first.")
            return False
        
        return True
    
    def build_android(self, variant="assembleDebug"):
        """Build Android app."""
        print(f"\n🤖 Building Android app ({variant})...")
        
        if not self.prereqs.get("android_studio"):
            print("✗ Android SDK not found")
            return False
        
        android_dir = PROJECT_PATH / "android"
        if not android_dir.exists():
            print("✗ Android project not found. Run setup_capacitor first.")
            return False
        
        # Build with Gradle
        if IS_WINDOWS:
            gradle_cmd = ".\\gradlew.bat"
        else:
            gradle_cmd = "./gradlew"
        
        result = run_cmd(f"cd android && {gradle_cmd} {variant}", capture=False)
        
        if result.returncode == 0:
            apk_path = android_dir / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
            print(f"✓ APK built: {apk_path}")
            return True
        else:
            print("✗ Build failed")
            return False
    
    def run_ios(self):
        """Run iOS app in simulator."""
        print("\n📱 Running iOS app in simulator...")
        
        if platform.system() != "Darwin":
            print("✗ iOS simulator requires macOS")
            return False
        
        simulator = self.config["ios"]["simulator"]
        result = run_cmd(f'npx cap run ios --target="{simulator}"', capture=False)
        
        return result.returncode == 0
    
    def run_android(self):
        """Run Android app in emulator."""
        print("\n📱 Running Android app in emulator...")
        
        result = run_cmd("npx cap run android", capture=False)
        return result.returncode == 0
    
    def setup_pwa(self):
        """Setup Progressive Web App."""
        print("\n🌐 Setting up PWA...")
        
        # Create manifest
        manifest = {
            "name": "NetworkBuster",
            "short_name": "NetBuster",
            "description": "Real-time network monitoring and management",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#000000",
            "theme_color": "#00ff00",
            "icons": [
                {
                    "src": "/icons/icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/icons/icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        }
        
        public_dir = PROJECT_PATH / "public"
        public_dir.mkdir(exist_ok=True)
        
        manifest_path = public_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✓ Manifest created: {manifest_path}")
        
        # Create service worker
        sw_content = '''
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activated');
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
'''
        
        sw_path = public_dir / "sw.js"
        with open(sw_path, "w") as f:
            f.write(sw_content)
        
        print(f"✓ Service Worker created: {sw_path}")
        print("✓ PWA setup complete")
        
        return True
    
    def deploy_all(self, env="production"):
        """Full mobile deployment pipeline."""
        print("\n" + "=" * 70)
        print("  🚀 FULL MOBILE DEPLOYMENT")
        print("=" * 70)
        
        steps = [
            ("Building web assets", lambda: self.build_web(env)),
            ("Syncing to mobile", self.sync_capacitor),
            ("Setting up PWA", self.setup_pwa)
        ]
        
        for step_name, step_func in steps:
            print(f"\n[{steps.index((step_name, step_func)) + 1}/{len(steps)}] {step_name}...")
            if not step_func():
                print(f"✗ Failed at: {step_name}")
                return False
        
        print("\n" + "=" * 70)
        print("  ✓ DEPLOYMENT COMPLETE")
        print("=" * 70)
        print("\n  Next steps:")
        print("    - iOS: python mobile_deployment.py --build-ios")
        print("    - Android: python mobile_deployment.py --build-android")
        print("    - Test PWA at: http://localhost:3000")
        
        return True


def show_menu():
    """Display mobile deployment menu."""
    print("\n" + "─" * 60)
    print("  📱 MOBILE DEPLOYMENT MANAGER")
    print("─" * 60)
    print("  [1] 📊 Show Status")
    print("  [2] ⚡ Setup Capacitor")
    print("  [3] 🔨 Build Web Assets")
    print("  [4] 🔄 Sync to Mobile")
    print("  [5] 🍎 Build iOS")
    print("  [6] 🤖 Build Android")
    print("  [7] 🌐 Setup PWA")
    print("  [8] 📱 Run iOS Simulator")
    print("  [9] 📱 Run Android Emulator")
    print("  [d] 🚀 Deploy All (Full Pipeline)")
    print("  [0] ❌ Exit")
    print("─" * 60)


def main():
    """Main entry point."""
    deployer = MobileDeployment()
    
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "  NetworkBuster Mobile Deployment".center(58) + "║")
    print("║" + "  iOS | Android | PWA".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    
    while True:
        show_menu()
        choice = input("\n  Select option: ").strip().lower()
        
        if choice == "1":
            deployer.show_status()
        elif choice == "2":
            deployer.setup_capacitor()
        elif choice == "3":
            env = input("  Environment (dev/staging/prod): ").strip() or "production"
            deployer.build_web(env)
        elif choice == "4":
            deployer.sync_capacitor()
        elif choice == "5":
            deployer.build_ios()
        elif choice == "6":
            deployer.build_android()
        elif choice == "7":
            deployer.setup_pwa()
        elif choice == "8":
            deployer.run_ios()
        elif choice == "9":
            deployer.run_android()
        elif choice == "d":
            env = input("  Environment (dev/staging/prod): ").strip() or "production"
            deployer.deploy_all(env)
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n⚠ Invalid option.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
