Invoke-WebRequest -Method POST http://127.0.0.1:3000/rephrase `
  -ContentType "application/json" `
  -Body '{"text":"Hello"}' | Select-Object -Expand Content
