Set-Location "C:\SPA-Project\backend"
$env:LLM_MODE="real"
$env:ALLWO_REAL_LLM="1"
$env:OPENAI_API_KEY=""
$env:OPENAI_MODEL="gpt-4o-mini"
python -m uvicorn app.main:app --port 3000