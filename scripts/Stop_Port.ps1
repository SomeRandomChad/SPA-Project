param(
  [Parameter(Mandatory = $true)]
  [int]$Port
)

$connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if (-not $connections) {
  Write-Host "No process is listening on port $Port"
  exit 0
}

$procIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique

foreach ($procId in $procIds) {
  try {
    $p = Get-Process -Id $procId -ErrorAction Stop
    Write-Host "Stopping PID $procId ($($p.ProcessName)) listening on port $Port..."
    Stop-Process -Id $procId -Force
  } catch {
    Write-Host "PID $procId not found anymore (already exited)."
  }
}

Write-Host "Done."