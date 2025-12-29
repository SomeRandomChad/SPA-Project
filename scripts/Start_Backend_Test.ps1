cd C:\SPA-Project\backend
$env:LLM_MODE="fake"
$env:ALLOW_REAL_LLM="0 "
$env:FAKE_STREAM_DELAY_MS="80"      # slower (try 80–200)
$env:FAKE_STREAM_CHUNK_SIZE="8"      # smaller chunk => more “typing”
python -m uvicorn app.main:app --reload --port 3000