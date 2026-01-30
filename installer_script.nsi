
; Software Distributor Installer Script
; Created by build_exe.py

!define APP_NAME "Software Distributor"
!define APP_VERSION "1.0.0"
!define PUBLISHER "NetworkBuster"
!define EXE_NAME "SoftwareDistributor.exe"

Name "${APP_NAME}"
OutFile "SoftwareDistributor_Setup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"

Page directory
Page instfiles

Section "Install"
    SetOutPath "$INSTDIR"
    File "dist\${EXE_NAME}"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Create Start Menu shortcut
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    
    ; Create Desktop shortcut
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\${EXE_NAME}"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk"
    RMDir "$SMPROGRAMS\${APP_NAME}"
    
    Delete "$DESKTOP\${APP_NAME}.lnk"
SectionEnd
