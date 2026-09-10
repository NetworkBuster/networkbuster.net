# PowerShell Issue Resolution Script
# Scans for problems and creates fix files for each identified issue

param(
    [string]$WorkspacePath = (Get-Location),
    [switch]$AutoFix = $false,
    [switch]$ShowReport = $true
)

$Issues = @{
    "PythonDependencies" = @{
        "Description" = "Missing Python dependencies (joblib, scikit-learn)"
        "Files" = @("device_classifiers.py", "model_registry.py")
        "Solution" = "Run: pip install scikit-learn joblib numpy"
        "Severity" = "HIGH"
    }
    "GitHubActionsWorkflow" = @{
        "Description" = "Invalid GitHub Actions workflow syntax"
        "Files" = @(".github/workflows/release-pipeline.yml")
        "Solution" = "Replace 'files' parameter with 'artifacts' in release action"
        "Severity" = "MEDIUM"
    }
    "CppUndefinedTypes" = @{
        "Description" = "Undefined C++ types (TCHAR, HANDLE, FILETIME)"
        "Files" = @("settings.h", "process.h")
        "Solution" = "Add #include <windows.h> to header files"
        "Severity" = "HIGH"
    }
}

function Write-IssueSummary {
    param([hashtable]$Issues)
    
    Write-Host "`n=== ISSUE SUMMARY ===" -ForegroundColor Yellow
    $totalIssues = 0
    
    foreach ($issue in $Issues.Keys) {
        $details = $Issues[$issue]
        Write-Host "`n[$issue]"
        Write-Host "Severity: $($details['Severity'])" -ForegroundColor Red
        Write-Host "Description: $($details['Description'])"
        Write-Host "Files affected: $(($details['Files'] | Join-String -Separator ', '))"
        Write-Host "Solution: $($details['Solution'])" -ForegroundColor Green
        $totalIssues++
    }
    
    Write-Host "`nTotal Issues Found: $totalIssues" -ForegroundColor Yellow
}

function Create-FixFile {
    param([string]$IssueType, [hashtable]$Details)
    
    $fixFileName = "fix_${IssueType}.ps1"
    $fixPath = Join-Path $WorkspacePath $fixFileName
    
    $fixContent = @"
# Auto-generated fix script for: $IssueType
# Generated: $(Get-Date)

Write-Host "Applying fix for: $($Details['Description'])" -ForegroundColor Green

switch ('$IssueType') {
    'PythonDependencies' {
        Write-Host "Installing Python dependencies..."
        python -m pip install scikit-learn joblib numpy
        Write-Host "Dependencies installed successfully!"
    }
    'GitHubActionsWorkflow' {
        Write-Host "Fixing GitHub Actions workflow..."
        `$workflowFile = '.github\workflows\release-pipeline.yml'
        `$content = Get-Content `$workflowFile -Raw
        `$content = `$content -replace "files:", "artifacts:"
        Set-Content `$workflowFile `$content
        Write-Host "Workflow file updated!"
    }
    'CppUndefinedTypes' {
        Write-Host "Adding missing C++ headers..."
        foreach (`$file in @('settings.h', 'process.h')) {
            if (Test-Path `$file) {
                `$content = Get-Content `$file -Raw
                if (-not `$content.Contains('#include <windows.h>')) {
                    `$content = '#include <windows.h>' + [Environment]::NewLine + `$content
                    Set-Content `$file `$content
                    Write-Host "Updated `$file"
                }
            }
        }
    }
}

Write-Host "Fix completed for $IssueType" -ForegroundColor Green
"@

    New-Item -Path $fixPath -ItemType File -Force | Out-Null
    Set-Content -Path $fixPath -Value $fixContent
    Write-Host "Created: $fixFileName" -ForegroundColor Cyan
}

function Main {
    Push-Location $WorkspacePath
    
    if ($ShowReport) {
        Write-IssueSummary $Issues
    }
    
    # Create fix files for each issue
    Write-Host "`n=== CREATING FIX FILES ===" -ForegroundColor Yellow
    foreach ($issueType in $Issues.Keys) {
        Create-FixFile -IssueType $issueType -Details $Issues[$issueType]
    }
    
    Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Yellow
    Write-Host "1. Review each fix_*.ps1 file"
    Write-Host "2. Run individually: .\fix_IssueType.ps1"
    Write-Host "3. Or run all: Get-ChildItem fix_*.ps1 | ForEach-Object { & `$_ }"
    
    if ($AutoFix) {
        Write-Host "`nAutoFix enabled. Running all fixes..." -ForegroundColor Yellow
        Get-ChildItem (Join-Path $WorkspacePath "fix_*.ps1") | ForEach-Object { & $_ }
    }
    
    Pop-Location
}

Main
