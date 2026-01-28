# Auto-generated fix script for: PythonDependencies
# Generated: 01/28/2026 06:49:33

Write-Host "Applying fix for: Missing Python dependencies (joblib, scikit-learn)" -ForegroundColor Green

switch ('PythonDependencies') {
    'PythonDependencies' {
        Write-Host "Installing Python dependencies..."
        python -m pip install scikit-learn joblib numpy
        Write-Host "Dependencies installed successfully!"
    }
    'GitHubActionsWorkflow' {
        Write-Host "Fixing GitHub Actions workflow..."
        $workflowFile = '.github\workflows\release-pipeline.yml'
        $content = Get-Content $workflowFile -Raw
        $content = $content -replace "files:", "artifacts:"
        Set-Content $workflowFile $content
        Write-Host "Workflow file updated!"
    }
    'CppUndefinedTypes' {
        Write-Host "Adding missing C++ headers..."
        foreach ($file in @('settings.h', 'process.h')) {
            if (Test-Path $file) {
                $content = Get-Content $file -Raw
                if (-not $content.Contains('#include <windows.h>')) {
                    $content = '#include <windows.h>' + [Environment]::NewLine + $content
                    Set-Content $file $content
                    Write-Host "Updated $file"
                }
            }
        }
    }
}

Write-Host "Fix completed for PythonDependencies" -ForegroundColor Green
