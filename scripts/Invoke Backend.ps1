Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:3000/rephrase" `
  -ContentType "application/json" `
  -Body '{"text":"Hello from PowerShell"}'