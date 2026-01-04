# SPA-Project — LLM Rephrase (SPA + API)

Single-page app (React) + backend API (FastAPI) that rephrases user input into four writing styles:

- Professional
- Casual
- Polite
- Social media

---

## Frozen API Contract

The canonical API contract is defined in:

SPA-Project/api/openapi.yml


This contract is **frozen** and enforced via automated tests.

---

## Request

```json
{ "text": "..." }

Response

{
  "professional": "...",
  "casual": "...",
  "polite": "...",
  "social": "..."
}

Streaming Support (SSE)

The backend supports incremental streaming responses using Server-Sent Events (SSE).
Streaming Endpoint

POST /rephrase/stream

    Uses text/event-stream

    Emits partial updates as the LLM generates output

    Ends with a final event matching the frozen response contract

    Fully cancellable by the client

SSE Event Types
Event	Description
partial	Incremental text update for a single style
final	Complete response (same shape as non-streaming API)
error	Normalized error payload

Example partial event payload:

{
  "style": "professional",
  "delta": "Please review"
}

Example final event payload:

{
  "professional": "...",
  "casual": "...",
  "polite": "...",
  "social": "..."
}

Repository Structure

frontend/ — React SPA (Create React App)
backend/  — FastAPI API + tests
scripts/  — PowerShell helpers for common tasks

Prerequisites

    Node.js (frontend)

    Python 3.12+ (tested on Windows with Python 3.14)

    PowerShell (Windows)

Backend Setup

From:

C:\SPA-Project\backend

Install dependencies and run tests:

python -m pip install -r requirements.txt
python -m pytest -q

Running the Backend (Fake LLM — Default)

Fake mode is the recommended default for development.
No tokens are used.

cd C:\SPA-Project\backend
python -m uvicorn app.main:app --reload --port 3000

Frontend Setup

From:

C:\SPA-Project\frontend

npm install
npm start

    Frontend: http://localhost:3001

    Backend: http://127.0.0.1:3000

Running End-to-End (Recommended Workflow)
Terminal 1 — Backend

cd C:\SPA-Project\backend
python -m uvicorn app.main:app --reload --port 3000

Terminal 2 — Frontend

cd C:\SPA-Project\frontend
npm start

Real LLM Mode (Azure OpenAI) — Token Safety

Real LLM usage is explicitly gated to prevent accidental spend.
Configuration Files

    backend/.env.example — committed (template)

    backend/.env — local only (DO NOT COMMIT)

Required Environment Variables (Azure OpenAI)

In backend/.env:

LLM_MODE=real
ALLOW_REAL_LLM=1

AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
AZURE_OPENAI_TIMEOUT_SECONDS=30

Notes

    AZURE_OPENAI_DEPLOYMENT is the Azure deployment name (e.g. gpt-5-chat)

    .env is loaded automatically at startup via python-dotenv

Start Backend in Real Mode

cd C:\SPA-Project\backend
python -m uvicorn app.main:app --reload --port 3000

Manual Request (PowerShell)

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:3000/rephrase" `
  -ContentType "application/json" `
  -Body '{"text":"Hello from PowerShell"}'

Error Handling (Normalized)

All errors return a stable shape:

{
  "code": "SOME_CODE",
  "message": "Human readable message",
  "details": []
}

Common Error Codes
Status	Code	Meaning
400	VALIDATION_ERROR	Invalid request
429	RATE_LIMIT_EXCEEDED	Upstream rate limiting
502	LLM_PROVIDER_FAILURE	Provider errors
504	LLM_TIMEOUT	Upstream timeout
500	INTERNAL_ERROR	Unexpected or invalid model output
Tests

Backend tests live in:

backend/tests

Run all tests:

cd C:\SPA-Project\backend
python -m pytest -q

Scripts (PowerShell)

Common helpers live in:

C:\SPA-Project\scripts

Examples:

    Start_Frontend.ps1

    Start_Backend_Real.ps1

    Start_Backend_Test.ps1

    Test_Backend.ps1

    Smoke_Rephrase.ps1

Run a script:

C:\SPA-Project\scripts\Test_Backend.ps1