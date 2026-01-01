param(
    [string]$Volume = 'K:',
    [uint64]$LimitBytes = 900000000000,
    [uint64]$WarningBytes = 850000000000
)

function Ensure-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) { throw "Administrator privileges required." }
}

try {
    Ensure-Admin
    Write-Output "Checking volume $Volume..."
    $vol = Get-Volume -DriveLetter ($Volume.TrimEnd(':')) -ErrorAction Stop
    if ($vol.FileSystem -ne 'NTFS') { throw "Volume $Volume is not NTFS (found $($vol.FileSystem)). Quotas require NTFS." }

    Write-Output "Enabling quota tracking on $Volume..."
    fsutil quota track $Volume

    # Use 'Everyone' SID S-1-1-0 to apply a default quota entry affecting all users
    $sid = 'S-1-1-0'
    Write-Output "Setting quota limit ${LimitBytes} bytes and threshold ${WarningBytes} bytes for SID $sid on $Volume..."
    fsutil quota modify $Volume $sid $LimitBytes $WarningBytes

    Write-Output "Querying quota entries on $Volume..."
    fsutil quota query $Volume
    Write-Output "NTFS per-user quota applied successfully."
} catch {
    Write-Error "Failed to apply quota: $_"
    exit 1
}