Set-Location "C:\SPA-Project\backend"
$env:LLM_MODE="real"
$env:ALLWO_REAL_LLM="1"
python -m uvicorn app.main:app --port 3000