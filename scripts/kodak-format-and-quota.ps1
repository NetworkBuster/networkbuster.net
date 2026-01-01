<#
kodak-format-and-quota.ps1
Backup D: to K:, format D: to NTFS, restore data, enable NTFS per-user quota (500 GB limit, 475 GB warning).
Run AS ADMIN. This script will prompt UAC when invoked via Start-Process -Verb RunAs.
#>

param(
    [string]$SourceDrive = 'D:',
    [string]$BackupRoot = 'K:\',
    [uint64]$LimitBytes = 500000000000,
    [uint64]$WarningBytes = 475000000000
)

function Ensure-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) { throw "Administrator privileges required. Re-run elevated." }
}

try {
    Ensure-Admin

    if ((Get-Volume -DriveLetter ($SourceDrive.TrimEnd(':')) -ErrorAction SilentlyContinue) -eq $null) {
        throw "Source drive $SourceDrive not found. Aborting."
    }

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $BackupDir = Join-Path $BackupRoot "backup-kodak-$timestamp"
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
    Write-Output "Backing up $SourceDrive to $BackupDir (this can take a long time)"

    $robolog = Join-Path $BackupDir "robocopy.log"
    $rcArgs = @("$SourceDrive\", "$BackupDir\", "/MIR", "/COPY:DAT", "/R:3", "/W:5", "/MT:8", "/V", "/ETA", "/LOG:$robolog")
    Write-Output "Running Robocopy: robocopy $($rcArgs -join ' ')"
    $rc = Start-Process -FilePath robocopy -ArgumentList $rcArgs -Wait -NoNewWindow -PassThru

    if ($rc.ExitCode -ge 8) {
        Write-Error "Robocopy failed with exit code $($rc.ExitCode). See $robolog"
        exit 1
    }

    Write-Output "Backup complete. Proceeding to format $SourceDrive to NTFS (quick)."
    # Format the volume quickly to NTFS
    Format-Volume -DriveLetter $SourceDrive.TrimEnd(':') -FileSystem NTFS -NewFileSystemLabel 'KODAK' -Confirm:$false -Force -ErrorAction Stop
    Write-Output "Format complete. Restoring files from backup to $SourceDrive"

    $restoreLog = Join-Path $BackupDir "robocopy-restore.log"
    $rcArgs2 = @("$BackupDir\", "$SourceDrive\", "/MIR", "/COPY:DAT", "/R:3", "/W:5", "/MT:8", "/V", "/ETA", "/LOG:$restoreLog")
    Write-Output "Running Robocopy restore: robocopy $($rcArgs2 -join ' ')"
    $rc2 = Start-Process -FilePath robocopy -ArgumentList $rcArgs2 -Wait -NoNewWindow -PassThru
    if ($rc2.ExitCode -ge 8) {
        Write-Error "Restore Robocopy failed with exit code $($rc2.ExitCode). See $restoreLog"
        exit 1
    }

    Write-Output "Restore complete. Enabling NTFS per-user quotas on $SourceDrive"
    # Enable and set quota for Everyone SID (S-1-1-0)
    fsutil quota track $SourceDrive
    fsutil quota modify $SourceDrive S-1-1-0 $LimitBytes $WarningBytes

    Write-Output "Verifying quota entries..."
    fsutil quota query $SourceDrive | Out-String | Write-Output

    Write-Output "All steps completed successfully. Backup preserved at: $BackupDir"
} catch {
    Write-Error "Script failed: $_"
    exit 1
}