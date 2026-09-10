"""
Build script to create executable from software_distributor.py
Uses PyInstaller to create standalone .exe file
"""

import os
import sys
import subprocess
import shutil


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print("✓ PyInstaller is installed")
        return True
    except ImportError:
        print("✗ PyInstaller not found")
        return False


def install_pyinstaller():
    """Install PyInstaller."""
    print("Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install PyInstaller")
        return False


def create_icon():
    """Create a simple icon file (optional)."""
    # This is a placeholder - you can add custom icon creation logic
    icon_path = "distributor_icon.ico"
    if os.path.exists(icon_path):
        return icon_path
    return None


def build_executable():
    """Build the executable using PyInstaller."""
    print("\n" + "=" * 60)
    print("Building Software Distributor Executable")
    print("=" * 60 + "\n")
    
    # Check PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("Cannot proceed without PyInstaller")
            return False
    
    # Build command
    script_name = "software_distributor.py"
    exe_name = "SoftwareDistributor"
    
    if not os.path.exists(script_name):
        print(f"✗ Error: {script_name} not found")
        return False
    
    print(f"Building {exe_name}.exe...")
    
    # PyInstaller command options
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window (GUI mode)
        "--name", exe_name,
        "--clean",  # Clean PyInstaller cache
    ]
    
    # Add icon if available
    icon_path = create_icon()
    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
    
    # Add the script
    cmd.append(script_name)
    
    try:
        # Run PyInstaller
        print(f"Command: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        
        print("\n✓ Build completed successfully!")
        print(f"\nExecutable location: dist/{exe_name}.exe")
        
        # Clean up build files (optional)
        cleanup = input("\nClean up build files? (y/n): ").lower()
        if cleanup == 'y':
            if os.path.exists("build"):
                shutil.rmtree("build")
                print("✓ Cleaned build directory")
            if os.path.exists(f"{exe_name}.spec"):
                os.remove(f"{exe_name}.spec")
                print("✓ Removed spec file")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


def build_with_console():
    """Build executable with console window (for debugging)."""
    print("\n" + "=" * 60)
    print("Building Software Distributor Executable (Console Mode)")
    print("=" * 60 + "\n")
    
    if not check_pyinstaller():
        if not install_pyinstaller():
            return False
    
    script_name = "software_distributor.py"
    exe_name = "SoftwareDistributor_Console"
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--console",  # Keep console window
        "--name", exe_name,
        "--clean",
        script_name
    ]
    
    try:
        subprocess.check_call(cmd)
        print(f"\n✓ Console version built: dist/{exe_name}.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        return False


def create_installer_script():
    """Create NSIS installer script (optional)."""
    nsis_script = """
; Software Distributor Installer Script
; Created by build_exe.py

!define APP_NAME "Software Distributor"
!define APP_VERSION "1.0.0"
!define PUBLISHER "NetworkBuster"
!define EXE_NAME "SoftwareDistributor.exe"

Name "${APP_NAME}"
OutFile "SoftwareDistributor_Setup.exe"
InstallDir "$PROGRAMFILES\\${APP_NAME}"

Page directory
Page instfiles

Section "Install"
    SetOutPath "$INSTDIR"
    File "dist\\${EXE_NAME}"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    ; Create Start Menu shortcut
    CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
    CreateShortcut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\${EXE_NAME}"
    CreateShortcut "$SMPROGRAMS\\${APP_NAME}\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
    
    ; Create Desktop shortcut
    CreateShortcut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\${EXE_NAME}"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\${EXE_NAME}"
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\\${APP_NAME}\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\${APP_NAME}"
    
    Delete "$DESKTOP\\${APP_NAME}.lnk"
SectionEnd
"""
    
    with open("installer_script.nsi", 'w') as f:
        f.write(nsis_script)
    
    print("✓ NSIS installer script created: installer_script.nsi")
    print("  Install NSIS and run: makensis installer_script.nsi")


def main():
    """Main build process."""
    print("\nSoftware Distributor - Executable Builder")
    print("Choose build option:")
    print("1. Build GUI executable (no console)")
    print("2. Build with console window (for debugging)")
    print("3. Build both versions")
    print("4. Create NSIS installer script")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        build_executable()
    elif choice == "2":
        build_with_console()
    elif choice == "3":
        build_executable()
        build_with_console()
    elif choice == "4":
        create_installer_script()
    elif choice == "5":
        print("Exiting...")
        return
    else:
        print("Invalid choice")
        return
    
    print("\n" + "=" * 60)
    print("Build process completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
