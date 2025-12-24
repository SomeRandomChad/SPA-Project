cd C:\SPA-Project\backend
$env:LLM_MODE="fake"
$env:ALLOW_REAL_LLM="0 "
python -m uvicorn app.main:app --port 3000