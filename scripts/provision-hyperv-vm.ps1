<#
.SYNOPSIS
    Provisions and upgrades a Hyper-V VM for high-performance AI and network workloads.
    Supports GPU Partitioning (GPU-PV) and SR-IOV.

.EXAMPLE
    .\scripts\provision-hyperv-vm.ps1 -VMName "NetworkBuster-Linux" -EnableGPU
#>

param(
    [string]$VMName = "NetworkBuster-Linux",
    [int]$Cores = 4,
    [int]$MemoryGB = 8,
    [switch]$EnableGPU,
    [switch]$EnableNetworkAcceleration
)

if (-not (Get-Service vmms -ErrorAction SilentlyContinue)) {
    Write-Error "Hyper-V service (vmms) is not available on this system."
    exit 1
}

$vm = Get-VM -Name $VMName -ErrorAction SilentlyContinue
if (-not $vm) {
    Write-Host "Creating new VM: $VMName..." -ForegroundColor Cyan
    New-VM -Name $VMName -Generation 2 -MemoryStartupBytes ($MemoryGB * 1GB)
} else {
    Write-Host "Upgrading existing VM: $VMName..." -ForegroundColor Cyan
    if ($vm.State -ne 'Off') {
        Write-Warning "VM is currently $($vm.State). Some settings require the VM to be OFF."
    }
}

# 1. Performance Tuning
Write-Host "Setting CPU Cores to $Cores..."
Set-VMProcessor -VMName $VMName -Count $Cores

Write-Host "Setting Memory to ${MemoryGB}GB (Static)..."
Set-VMMemory -VMName $VMName -DynamicMemoryEnabled $false -StartupBytes ($MemoryGB * 1GB)

# 2. Network Acceleration
if ($EnableNetworkAcceleration) {
    Write-Host "Enabling SR-IOV and MacAddressSpoofing..."
    Get-VMNetworkAdapter -VMName $VMName | Set-VMNetworkAdapter -IovWeight 100 -MacAddressSpoofing On
}

# 3. GPU Partitioning (GPU-PV)
if ($EnableGPU) {
    Write-Host "Enabling GPU Partitioning..." -ForegroundColor Yellow
    
    # Check if GPU is assignable
    $gpu = Get-VMHostAssignableDevice | Where-Object { $_.InstancePath -like "*PCI*" }
    if (-not $gpu) {
        Write-Warning "No assignable GPU found. Ensure your host GPU supports partitioning and is not in use."
    } else {
        Add-VMAssignableDevice -VMName $VMName -LocationPath $gpu.LocationPath
        Write-Host "GPU assigned successfully." -ForegroundColor Green
    }
}

# 4. Final Verification
Write-Host "`nUpgrade Complete for $VMName" -ForegroundColor Green
Get-VM -Name $VMName | Select-Object Name, State, CPUUsage, MemoryUsage | Format-Table
