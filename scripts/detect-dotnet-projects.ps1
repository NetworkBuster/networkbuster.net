<#
Detect .NET projects in the workspace and update .vscode/launch.json with sane Launch configs.
Usage:
  .\scripts\detect-dotnet-projects.ps1 [-DryRun]

Behavior:
 - Searches recursively for *.csproj files (excluding bin/obj paths)
 - For each project, attempts to determine AssemblyName and TargetFramework (first if multiple)
 - Infers the typical output path: <project>/bin/Debug/<TF>/<assembly>.dll
 - If output doesn't exist, optionally runs `dotnet build <proj>` to produce outputs
 - Updates .vscode/launch.json by replacing the sample Launch entry with per-project entries
 - Backups the previous launch.json to .vscode/launch.json.bak
#>
param(
  [switch]$DryRun
)

function Get-Projects {
  Get-ChildItem -Path (Get-Location).Path -Filter *.csproj -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\bin\\|\\obj\\" }
}

function Parse-CsProj([string]$path) {
  try {
    [xml]$xml = Get-Content -Path $path -Raw -ErrorAction Stop
    $ns = @{ms = $xml.Project.NamespaceURI}
    $assemblyName = ($xml.Project.PropertyGroup.AssemblyName | Where-Object { $_ }) -join ''
    if (-not $assemblyName) { $assemblyName = [System.IO.Path]::GetFileNameWithoutExtension($path) }
    $tf = ($xml.Project.PropertyGroup.TargetFramework | Where-Object { $_ }) -join ''
    if (-not $tf) {
      $tfs = ($xml.Project.PropertyGroup.TargetFrameworks | Where-Object { $_ }) -join ''
      if ($tfs) { $tf = ($tfs -split ';')[0] }
    }
    return @{ ProjectPath = $path; ProjectDir = (Split-Path $path -Parent); Assembly = $assemblyName; TF = $tf }
  } catch {
    Write-Warning "Failed to parse $path: $($_)"
    return $null
  }
}

function Infer-Output([hashtable]$info) {
  $projDir = $info.ProjectDir
  $assembly = $info.Assembly
  $tf = $info.TF
  if ($tf) {
    $dll = Join-Path $projDir "bin\Debug\$tf\$assembly.dll"
  } else {
    # try to find any net*/ paths
    $candidates = Get-ChildItem -Path (Join-Path $projDir 'bin\Debug') -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^net' }
    if ($candidates -and $candidates.Count -gt 0) {
      $dll = Join-Path $projDir "bin\Debug\$($candidates[0].Name)\$assembly.dll"
    } else {
      $dll = Join-Path $projDir "bin\Debug\$assembly.dll"
    }
  }
  return $dll
}

function Update-LaunchJson([array]$projects, [switch]$dryRun) {
  $launchPath = Join-Path -Path (Get-Location).Path -ChildPath '.vscode\launch.json'
  if (-not (Test-Path $launchPath)) {
    Write-Host "No existing $launchPath found; creating a new one." -ForegroundColor Cyan
    $base = @{ version = '0.2.0'; configurations = @() }
  } else {
    $base = Get-Content -Raw -Path $launchPath | ConvertFrom-Json -ErrorAction Stop
    # backup
    Copy-Item -Path $launchPath -Destination "$launchPath.bak" -Force
  }

  # Remove any existing auto-generated entries we created before (marker: generatedBy=detect-dotnet-projects)
  $filtered = @()
  foreach ($cfg in $base.configurations) {
    if (-not ($cfg.generatedBy -and $cfg.generatedBy -eq 'detect-dotnet-projects')) { $filtered += $cfg }
  }

  foreach ($p in $projects) {
    $name = ".NET: Launch - $([IO.Path]::GetFileNameWithoutExtension($p.ProjectPath))"
    $program = $p.OutputDll
    $cfg = @{
      name = $name
      type = 'coreclr'
      request = 'launch'
      preLaunchTask = 'build'
      program = $program
      args = @()
      cwd = '${workspaceFolder}'
      stopAtEntry = $false
      console = 'integratedTerminal'
      justMyCode = $true
      generatedBy = 'detect-dotnet-projects'
    }
    $filtered += $cfg
  }

  $base.configurations = $filtered

  if ($dryRun) {
    Write-Host "Dry-run: would write the following launch.json content:" -ForegroundColor Cyan
    $base | ConvertTo-Json -Depth 10 | Write-Output
    return
  }

  $base | ConvertTo-Json -Depth 10 | Set-Content -Path $launchPath -Encoding UTF8
  Write-Host "Updated $launchPath with $($projects.Count) launch configurations. Backup at $launchPath.bak" -ForegroundColor Green
}

# Main
$projs = Get-Projects | ForEach-Object { Parse-CsProj $_.FullName } | Where-Object { $_ }
if (-not $projs -or $projs.Count -eq 0) {
  Write-Host "No .csproj files found in workspace." -ForegroundColor Yellow
  exit 0
}

$projectsToWrite = @()
foreach ($p in $projs) {
  $dll = Infer-Output $p
  if (-not (Test-Path $dll)) {
    Write-Host "Output not found for project $($p.ProjectPath). Attempting to build to produce outputs..." -ForegroundColor Yellow
    $b = dotnet build $p.ProjectPath
    if ($LASTEXITCODE -ne 0) { Write-Warning "dotnet build failed for $($p.ProjectPath). The inferred output path may not exist." }
  }
  $dll = Infer-Output $p # re-infer
  $p.Add('OutputDll', $dll)
  $projectsToWrite += $p
}

if ($projectsToWrite.Count -eq 0) { Write-Host 'No projects to add to launch.json' -ForegroundColor Yellow; exit 0 }

# Update launch.json
Update-LaunchJson -projects $projectsToWrite -dryRun:$DryRun

# Print summary
foreach ($x in $projectsToWrite) {
  Write-Host "Project: $($x.ProjectPath) -> Output: $($x.OutputDll)" -ForegroundColor Cyan
}

Write-Host "Done." -ForegroundColor Green
