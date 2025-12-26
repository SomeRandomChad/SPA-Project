# SPA-Project — LLM Rephrase (SPA + API)

Single-page app (React) + backend API (FastAPI) that rephrases user input into four writing styles:

- Professional
- Casual
- Polite
- Social media

## Frozen API Contract found in SPA-Project\api\openapi.yml

## Request
```json
{ "text": "..." }

## Response
{
  "professional": "...",
  "casual": "...",
  "polite": "...",
  "social": "..."
}

## Repo Structure
    frontend/ — React SPA (Create React App)
    backend/ — FastAPI API + tests
    scripts/ — PowerShell helpers for common tasks

## Prerequisites
    Node.js (for frontend)
    Python 3.12+ (project tested on Windows with Python 3.14)
    PowerShell (Windows)

## Backend Setup

    From C:\SPA-Project\backend:

    python -m pip install -r requirements.txt
    python -m pytest -q

    Run backend (Fake mode — default, no token usage)

    Fake mode is the recommended default for development.

    cd C:\SPA-Project\backend
    python -m uvicorn app.main:app --reload --port 3000

    You can also use the provided scripts (see Scripts below).

## Frontend Setup
    From C:\SPA-Project\frontend:
    
    npm install
    npm start
    
    default dev URL is:
    http://localhost:3001
    The frontend calls the backend at:
    http://127.0.0.1:3000

## Running End-to-End (Recommended Workflow)

    Terminal 1 (backend):
    cd C:\SPA-Project\backend
    python -m uvicorn app.main:app --reload --port 3000


    Terminal 2 (frontend):
    cd C:\SPA-Project\frontend
    npm start

## Real LLM Mode (Azure OpenAI) — Token/Spend Safety

    The backend supports Fake and Real modes. Real mode is guarded by an explicit opt-in to prevent accidental spend.

    Configuration files
    backend/.env.example — committed (template, no secrets)
    backend/.env — local only (DO NOT COMMIT), is included in .gitignore

## Required env vars for Azure OpenAI

    In backend/.env (local only):

    LLM_MODE=real
    ALLOW_REAL_LLM=1

    AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
    AZURE_OPENAI_API_KEY=<your-key>
    AZURE_OPENAI_API_VERSION=2024-10-21
    AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
    AZURE_OPENAI_TIMEOUT_SECONDS=30
    Notes:
    AZURE_OPENAI_DEPLOYMENT is the deployment name in Azure (often set to something like gpt-5-chat).
    The backend loads .env at startup (via python-dotenv).

## Start backend in Real mode
    cd C:\SPA-Project\backend
    python -m uvicorn app.main:app --reload --port 3000

## One manual request (PowerShell)
    Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:3000/rephrase" `
    -ContentType "application/json" `
    -Body '{"text":"Hello from PowerShell"}'

## Error Handling (Normalized)

## The API returns a stable error shape:
    {
    "code": "SOME_CODE",
    "message": "Human readable message",
    "details": []
    }

    Common cases:
    400 VALIDATION_ERROR — request validation failures
    429 RATE_LIMIT_EXCEEDED — upstream rate limiting (may include Retry-After)
    502 LLM_PROVIDER_FAILURE — upstream provider errors (auth, deployment not found, connection issues)
    504 LLM_TIMEOUT — upstream timeout
    500 INTERNAL_ERROR — unexpected errors or invalid model output

## Tests
    Backend tests live in backend/tests.
    Run all tests:
    cd C:\SPA-Project\backend
    python -m pytest -q


Scripts (PowerShell)
    Common helpers are in C:\SPA-Project\scripts:
    Examples:
    Start_Frontend.ps1
    Start_Backend_Real.ps1 / Start_Backend_Test.ps1
    Test_Backend.ps1 / Test_Backend_Debug.ps1
    Smoke_Rephrase.ps1
    Run a script like:
    C:\SPA-Project\scripts\Test_Backend.ps1

