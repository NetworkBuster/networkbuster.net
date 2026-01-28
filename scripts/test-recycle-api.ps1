<# Simple test for recycle API (requires server running) #>
$payload = @{ items = @( @{ name = 'pizza box'; context='greasy' }, @{ name = 'plastic bottle' } ); location='94107'; userId='test1' }
try {
  $r = Invoke-WebRequest -Uri 'http://localhost:3001/api/recycle/recommend' -Method Post -Body ($payload | ConvertTo-Json -Depth 5) -ContentType 'application/json' -TimeoutSec 5
  Write-Output $r.Content
} catch { Write-Error $_.Exception.Message }
