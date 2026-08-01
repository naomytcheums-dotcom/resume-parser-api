# Resume Parser API

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat&logo=pydantic&logoColor=white)
![OpenAI SDK](https://img.shields.io/badge/OpenAI_SDK-412991?style=flat&logo=openai&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=flat&logo=render&logoColor=white)

**[Live API](https://resume-parser-api-h04v.onrender.com)** — try it interactively at **[/docs](https://resume-parser-api-h04v.onrender.com/docs)**

A small, focused REST API: upload a resume (PDF, DOCX, or TXT), get back structured JSON — name, contact info, skills, work experience, and education. Built as a standalone backend service — no frontend, no database. Interactive documentation (Swagger UI) is generated automatically by FastAPI.

## Endpoint

### `POST /api/parse-resume`

**Headers**
- `X-API-Key` — required only if `API_ACCESS_KEY` is set on the server

**Body** — `multipart/form-data`
- `file` — the resume file, `.pdf`, `.docx`, or `.txt`

**Response**
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "phone": "+1 555 123 4567",
  "location": "San Francisco, CA",
  "summary": "Backend engineer with 6 years of experience...",
  "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
  "experience": [
    {
      "title": "Senior Backend Engineer",
      "company": "Acme Corp",
      "duration": "Jan 2021 - Present",
      "description": "Led the migration to a microservices architecture..."
    }
  ],
  "education": [
    {
      "degree": "B.S. in Computer Science",
      "institution": "University of California, Berkeley",
      "year": "2018"
    }
  ]
}
```

Every field defaults to an empty string or empty list if it can't be found in the document — the API never invents data that isn't in the source resume.

**Errors**
- `422` — unsupported file type, empty file, or a file with no extractable text (e.g. a scanned image PDF with no text layer)
- `401` — missing or invalid `X-API-Key` (only if access control is enabled)
- `502` — the LLM request failed (quota, network, misconfigured key) — the response includes a clean, truncated reason

### `GET /api/health`

Returns `{"status": "ok"}`. Useful for uptime checks.

### `GET /docs`

Interactive Swagger UI — try the API directly from your browser.

## Example

```bash
curl -X POST https://resume-parser-api-h04v.onrender.com/api/parse-resume \
  -H "X-API-Key: your-key-if-set" \
  -F "file=@resume.pdf"
```

## Tech stack

FastAPI, Pydantic, pypdf (PDF text extraction), python-docx (DOCX text extraction), OpenAI-compatible LLM client (works with OpenAI, Google Gemini, Groq, or any OpenAI-compatible endpoint).

## Running locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in your own LLM key
uvicorn app.main:app --reload --port 8097
```

Then open `http://localhost:8097/docs` to try it interactively.

## Deploying

**Render:**
- New Web Service, root directory: repo root (no subfolder)
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables: `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`, `API_ACCESS_KEY` (optional), `CORS_ORIGINS`

No frontend, no database — this is a pure backend API, deployable on its own.

## Status

This is an MVP built for portfolio purposes. It requires your own LLM API key — no credentials are shared or included. `API_ACCESS_KEY` is optional; leave it empty for an open demo, or set it to require callers to authenticate. Note: scanned/image-only PDFs (no text layer) can't be parsed — this uses text extraction, not OCR.
