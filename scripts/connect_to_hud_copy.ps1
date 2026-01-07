æparam(
    [string]$Token = ""
)

$url = "https://networkbuster-a0su5rt4h-networkbuster.vercel.app/hud.html"
$headers = @{}

if ($Token) {
    $headers["Authorization"] = "Bearer $Token"
    Write-Host "Using provided authentication token." -ForegroundColor Cyan
} else {
    Write-Host "No token provided. Request may fail if authentication is required." -ForegroundColor Yellow
}

Write-Host "Connecting to remote host: $url" -ForegroundColor Gray
try {
    # Using -UserAgent to mimic a browser if needed, though default is usually fine
    $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get
    Write-Host "Successfully connected!" -ForegroundColor Green
    return $response
} catch {
    $status = $_.Exception.Response.StatusCode
    if ($status -eq "Unauthorized") {
        Write-Error "Failed to connect: 401 Unauthorized. Please provide a valid -Token."
    } else {
        Write-Error "Failed to connect: $($_.Exception.Message)"
    }
}
æ*cascade08"(64854563714512de5f76da405d292f680e540e792>file:///c:/repository/src/networkbuster.net/connect_to_hud.ps1:+file:///c:/repository/src/networkbuster.net