#Start_Backend First
param(
  [string]$Text = "Hello"
)

$body = @{ text = $Text } | ConvertTo-Json
Invoke-WebRequest -Method POST "http://127.0.0.1:3000/rephrase" `
  -ContentType "application/json" `
  -Body $body | Select-Object -Expand Content