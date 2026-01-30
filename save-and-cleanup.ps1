<#
.SYNOPSIS
    NetworkBuster Universal Save & Cleanup Script
.DESCRIPTION
    Updates, cleans, and saves NetworkBuster project to all available drives
#>

param(
    [switch]$SkipGit,
    [switch]$SkipBackup,
    [switch]$CleanOnly,
    [string]$BackupPath = ""
)

$ErrorActionPreference = "Continue"
$ProjectRoot = "C:\Users\daypi\networkbuster.net"

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     NETWORKBUSTER UNIVERSAL SAVE & CLEANUP SYSTEM          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Check if running in project directory
if (-not (Test-Path $ProjectRoot)) {
    Write-Host "❌ Project directory not found: $ProjectRoot" -ForegroundColor Red
    exit 1
}

Set-Location $ProjectRoot

# ============================================
# PHASE 1: CLEANUP OPERATION
# ============================================
Write-Host "`n[PHASE 1] 🧹 CLEANUP OPERATION" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$cleanupItems = @{
    "Node Modules Cache" = @("node_modules\.cache", ".npm")
    "Build Artifacts" = @("dist", "build", ".next", "out")
    "Logs" = @("*.log", "logs", "npm-debug.log*")
    "Temp Files" = @("*.tmp", "*.temp", ".DS_Store", "Thumbs.db")
    "Python Cache" = @("__pycache__", "*.pyc", "*.pyo", ".pytest_cache")
    "Editor Temp" = @(".vscode-test", "*.swp", "*.swo", "*~")
}

$totalCleaned = 0
$cleanedFiles = 0

foreach ($category in $cleanupItems.Keys) {
    Write-Host "`n  Cleaning: $category..." -ForegroundColor Cyan
    
    foreach ($pattern in $cleanupItems[$category]) {
        try {
            $items = Get-ChildItem -Path $ProjectRoot -Recurse -Force -Include $pattern -ErrorAction SilentlyContinue
            
            foreach ($item in $items) {
                try {
                    $size = 0
                    if ($item.PSIsContainer) {
                        $size = (Get-ChildItem -Path $item.FullName -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                        Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
                    } else {
                        $size = $item.Length
                        Remove-Item -Path $item.FullName -Force -ErrorAction SilentlyContinue
                    }
                    
                    if ($size) {
                        $totalCleaned += $size
                        $cleanedFiles++
                        $sizeStr = "{0:N2} MB" -f ($size / 1MB)
                        Write-Host "    ✓ Removed: $($item.Name) ($sizeStr)" -ForegroundColor DarkGray
                    }
                } catch {
                    Write-Host "    ⚠ Skipped: $($item.Name)" -ForegroundColor DarkYellow
                }
            }
        } catch {
            Write-Host "    ⚠ Pattern not found: $pattern" -ForegroundColor DarkYellow
        }
    }
}

$cleanedMB = [math]::Round($totalCleaned / 1MB, 2)
Write-Host "`n  ✅ Cleanup Complete!" -ForegroundColor Green
Write-Host "     Files Removed: $cleanedFiles" -ForegroundColor White
Write-Host "     Space Freed: $cleanedMB MB" -ForegroundColor White

if ($CleanOnly) {
    Write-Host "`n✅ Cleanup-only mode complete!" -ForegroundColor Green
    exit 0
}

# ============================================
# PHASE 2: GIT OPERATIONS
# ============================================
if (-not $SkipGit) {
    Write-Host "`n[PHASE 2] 📦 GIT SAVE OPERATION" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

    # Check if git is available
    $gitAvailable = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
    
    if ($gitAvailable) {
        # Check if this is a git repository
        $isGitRepo = Test-Path (Join-Path $ProjectRoot ".git")
        
        if ($isGitRepo) {
            Write-Host "`n  Checking git status..." -ForegroundColor Cyan
            
            # Get status
            $status = git status --porcelain
            
            if ($status) {
                Write-Host "    Changes detected:" -ForegroundColor White
                $status | ForEach-Object { Write-Host "      $_" -ForegroundColor DarkGray }
                
                # Add all changes
                Write-Host "`n  Adding changes to git..." -ForegroundColor Cyan
                git add -A
                Write-Host "    ✓ Files staged" -ForegroundColor Green
                
                # Commit with timestamp
                $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                $commitMsg = "Auto-save: Update and cleanup - $timestamp"
                
                Write-Host "`n  Committing changes..." -ForegroundColor Cyan
                git commit -m $commitMsg
                Write-Host "    ✓ Changes committed" -ForegroundColor Green
                
                # Check for remote
                $hasRemote = (git remote) -ne $null
                if ($hasRemote) {
                    Write-Host "`n  Pushing to remote..." -ForegroundColor Cyan
                    try {
                        git push
                        Write-Host "    ✓ Pushed to remote" -ForegroundColor Green
                    } catch {
                        Write-Host "    ⚠ Push failed (may need authentication)" -ForegroundColor Yellow
                    }
                }
            } else {
                Write-Host "    ✓ No changes to commit" -ForegroundColor Green
            }
        } else {
            Write-Host "    ⚠ Not a git repository" -ForegroundColor Yellow
            Write-Host "    Initializing git repository..." -ForegroundColor Cyan
            git init
            git add -A
            git commit -m "Initial commit: NetworkBuster project"
            Write-Host "    ✓ Repository initialized" -ForegroundColor Green
        }
    } else {
        Write-Host "    ⚠ Git not available, skipping version control" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[PHASE 2] ⏭️  Skipping Git Operations" -ForegroundColor DarkGray
}

# ============================================
# PHASE 3: MULTI-DRIVE BACKUP
# ============================================
if (-not $SkipBackup) {
    Write-Host "`n[PHASE 3] 💾 MULTI-DRIVE BACKUP" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

    # Get all available drives
    $drives = Get-PSDrive -PSProvider FileSystem | Where-Object { 
        $_.Used -ne $null -and 
        $_.Name -ne 'C' -and 
        $_.Free -gt 1GB 
    }

    if ($drives.Count -eq 0) {
        Write-Host "    ⚠ No additional drives available for backup" -ForegroundColor Yellow
    } else {
        Write-Host "`n  Available drives for backup:" -ForegroundColor Cyan
        $drives | ForEach-Object {
            $freeGB = [math]::Round($_.Free / 1GB, 2)
            Write-Host "    📁 $($_.Name): ($($_.Root)) - ${freeGB} GB free" -ForegroundColor White
        }

        $timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
        $backupFolderName = "NetworkBuster_Backup_$timestamp"
        
        # Exclude patterns for backup
        $excludePatterns = @(
            "node_modules",
            ".git",
            ".venv",
            "__pycache__",
            "*.log",
            ".DS_Store",
            "Thumbs.db"
        )

        foreach ($drive in $drives) {
            $backupRoot = if ($BackupPath) { 
                Join-Path $drive.Root $BackupPath 
            } else { 
                Join-Path $drive.Root "Backups" 
            }
            
            $backupPath = Join-Path $backupRoot $backupFolderName

            Write-Host "`n  Backing up to $($drive.Name):..." -ForegroundColor Cyan
            
            try {
                # Create backup directory
                if (-not (Test-Path $backupRoot)) {
                    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
                }
                
                New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
                
                # Copy files with exclusions
                Write-Host "    Copying files..." -ForegroundColor DarkGray
                
                $robocopyArgs = @(
                    $ProjectRoot,
                    $backupPath,
                    "/E",           # Copy subdirectories including empty ones
                    "/NFL",         # No file list
                    "/NDL",         # No directory list
                    "/NJH",         # No job header
                    "/NJS",         # No job summary
                    "/NC",          # No class
                    "/NS",          # No size
                    "/NP"           # No progress
                )
                
                # Add exclusions
                foreach ($pattern in $excludePatterns) {
                    $robocopyArgs += "/XD"
                    $robocopyArgs += $pattern
                }
                
                $result = robocopy @robocopyArgs 2>&1
                
                # Create backup manifest
                $manifest = @{
                    BackupDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    SourcePath = $ProjectRoot
                    BackupPath = $backupPath
                    Drive = $drive.Name
                    ExcludedPatterns = $excludePatterns
                } | ConvertTo-Json -Depth 3
                
                $manifestPath = Join-Path $backupPath "BACKUP_MANIFEST.json"
                $manifest | Out-File -FilePath $manifestPath -Encoding UTF8
                
                # Calculate backup size
                $backupSize = (Get-ChildItem -Path $backupPath -Recurse -Force | Measure-Object -Property Length -Sum).Sum
                $backupSizeMB = [math]::Round($backupSize / 1MB, 2)
                
                Write-Host "    ✅ Backup complete! ($backupSizeMB MB)" -ForegroundColor Green
                Write-Host "       Location: $backupPath" -ForegroundColor DarkGray
                
            } catch {
                Write-Host "    ❌ Backup failed: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "`n[PHASE 3] ⏭️  Skipping Backup Operations" -ForegroundColor DarkGray
}

# ============================================
# PHASE 4: GENERATE REPORT
# ============================================
Write-Host "`n[PHASE 4] 📊 GENERATING REPORT" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

$reportPath = Join-Path $ProjectRoot "SAVE_CLEANUP_REPORT.md"
$reportDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$report = @"
# NetworkBuster Save & Cleanup Report
**Generated:** $reportDate

## Cleanup Summary
- **Files Removed:** $cleanedFiles
- **Space Freed:** $cleanedMB MB

## Git Status
$(if (-not $SkipGit) {
    if ($gitAvailable -and $isGitRepo) {
        "- ✅ Changes committed to git
- Commit: Auto-save $reportDate"
    } else {
        "- ⚠️ Git operations unavailable"
    }
} else {
    "- ⏭️ Skipped"
})

## Backup Status
$(if (-not $SkipBackup) {
    if ($drives.Count -gt 0) {
        "- ✅ Backups created on $($drives.Count) drive(s)
- Backup folder: $backupFolderName"
    } else {
        "- ⚠️ No additional drives available"
    }
} else {
    "- ⏭️ Skipped"
})

## Project Statistics
- **Project Path:** $ProjectRoot
- **Total Drives:** $((Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -ne $null }).Count)

## Next Steps
1. Verify backup integrity
2. Test restored files if needed
3. Review git commit history
4. Monitor disk space usage

---
*Report generated by NetworkBuster Universal Save & Cleanup System*
"@

$report | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "`n  ✅ Report saved to: SAVE_CLEANUP_REPORT.md" -ForegroundColor Green

# ============================================
# FINAL SUMMARY
# ============================================
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  ✅ ALL OPERATIONS COMPLETE                 ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "   • Cleaned: $cleanedFiles files ($cleanedMB MB)" -ForegroundColor White
Write-Host "   • Git: $(if (-not $SkipGit -and $gitAvailable) { 'Saved ✓' } else { 'Skipped' })" -ForegroundColor White
Write-Host "   • Backups: $(if (-not $SkipBackup) { "$($drives.Count) drive(s) ✓" } else { 'Skipped' })" -ForegroundColor White
Write-Host "   • Report: $reportPath" -ForegroundColor White

Write-Host "`n🎉 Project saved and cleaned successfully!" -ForegroundColor Green
Write-Host ""
