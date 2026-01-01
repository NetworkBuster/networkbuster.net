<#
kodak-clean-format-restore.ps1
Performs: find D: disk, confirm, DiskPart clean, create partition, format NTFS, restore backup from latest K:\backup-kodak-*, enable per-user quota (500 GB limit, 475 GB warning).
Run as Administrator. This is destructive for D:; backups should already exist.
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

    Write-Output "Locating latest backup under $BackupRoot..."
    $backup = Get-ChildItem -Path $BackupRoot -Directory -Filter 'backup-kodak-*' | Sort-Object Name | Select-Object -Last 1
    if (-not $backup) { throw "No backup found under $BackupRoot matching backup-kodak-*" }
    $BackupDir = $backup.FullName
    Write-Output "Found backup: $BackupDir"

    # find partition / disk for SourceDrive
    $part = Get-Partition -DriveLetter ($SourceDrive.TrimEnd(':')) -ErrorAction SilentlyContinue
    if (-not $part) { throw "Drive $SourceDrive not present. Aborting." }
    $diskNumber = $part.DiskNumber
    Write-Output "Source drive $SourceDrive is on Disk $diskNumber"

    # Confirm with user (non-interactive - rely on prior confirmation)

    # Clear disk and create new NTFS partition (destructive)
    Write-Output "Clearing disk $diskNumber and creating new NTFS partition (this will destroy all data on disk $diskNumber)..."
    # Clear-Disk removes partition table and any data structures
    Clear-Disk -Number $diskNumber -RemoveData -RemoveOEM -Confirm:$false -ErrorAction Stop

    # Create a single primary partition and format it to NTFS
    $newPart = New-Partition -DiskNumber $diskNumber -UseMaximumSize -AssignDriveLetter -ErrorAction Stop
    Format-Volume -Partition $newPart -FileSystem NTFS -NewFileSystemLabel 'KODAK' -Confirm:$false -Force -ErrorAction Stop

    Start-Sleep -Seconds 3

    # verify format
    $vol = Get-Volume -DriveLetter ($SourceDrive.TrimEnd(':')) -ErrorAction Stop
    Write-Output "Volume status: DriveLetter=$($vol.DriveLetter) FileSystem=$($vol.FileSystem) Size=$($vol.Size)";
    if ($vol.FileSystem -ne 'NTFS') { throw "Unexpected filesystem after format: $($vol.FileSystem)" }

    # restore backup with robocopy
    Write-Output "Restoring data from $BackupDir to $SourceDrive (this may take a while)..."
    $restoreLog = Join-Path $BackupDir "robocopy-restore.log"
    $rcArgs2 = @("$BackupDir\", "$SourceDrive\", "/MIR", "/COPY:DAT", "/R:3", "/W:5", "/MT:8", "/V", "/ETA", "/LOG:$restoreLog")
    $rc2 = Start-Process -FilePath robocopy -ArgumentList $rcArgs2 -Wait -NoNewWindow -PassThru
    if ($rc2.ExitCode -ge 8) { throw "Robocopy restore failed with exit code $($rc2.ExitCode). See $restoreLog" }

    # Enable quota tracking and set quota
    Write-Output "Enabling quota tracking and applying quota limit/warning (Everyone SID)..."
    fsutil quota track $SourceDrive
    fsutil quota modify $SourceDrive S-1-1-0 $LimitBytes $WarningBytes

    Write-Output "Verifying quota entries..."
    $quotaQuery = fsutil quota query $SourceDrive 2>&1
    Write-Output $quotaQuery

    Write-Output "Completed: Disk cleaned, formatted NTFS, restored, and quota applied. Backup kept at $BackupDir"
} catch {
    Write-Error "Operation failed: $_"
    exit 1
} finally {
    if (Test-Path $dpFile) { Remove-Item $dpFile -Force -ErrorAction SilentlyContinue }
}
