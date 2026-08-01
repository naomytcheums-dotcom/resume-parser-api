import json
import re

from app.config import settings
from app.services.llm_client import LLMNotConfiguredError, get_client

SYSTEM_PROMPT = """You extract structured data from resumes/CVs.

Respond with ONLY valid JSON, no markdown fences, in this exact shape:
{
  "name": "full name",
  "email": "email address",
  "phone": "phone number",
  "location": "city, country",
  "summary": "a 1-2 sentence professional summary",
  "skills": ["skill 1", "skill 2"],
  "experience": [
    {"title": "job title", "company": "company name", "duration": "e.g. Jan 2020 - Present", "description": "brief description"}
  ],
  "education": [
    {"degree": "degree name", "institution": "school name", "year": "e.g. 2019"}
  ]
}

Rules:
- Use "" for any string field you cannot find, and [] for any list you cannot find.
- Never invent information not present in the resume text.
- List experience and education entries in the order they appear in the source, most recent first if that's how the resume is structured.
- Keep descriptions concise — one or two sentences per role."""


class ResumeParsingError(RuntimeError):
    pass


def _strip_code_fence(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text


def _as_str(value) -> str:
    return str(value).strip() if value is not None else ""


def _as_str_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def _as_entry_list(value, keys: list[str]) -> list[dict]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        if not isinstance(item, dict):
            continue
        result.append({key: _as_str(item.get(key)) for key in keys})
    return result


def parse_resume_text(text: str) -> dict:
    try:
        client = get_client()
    except LLMNotConfiguredError as exc:
        raise ResumeParsingError(str(exc)) from exc

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text[:15000]},
            ],
            temperature=0.1,
            max_tokens=2048,
        )
    except Exception as exc:  # noqa: BLE001 — surfaced as a clean API error
        message = str(exc).split("\n")[0][:200]
        raise ResumeParsingError(f"Resume parsing request failed: {message}") from exc

    content = response.choices[0].message.content or "{}"
    try:
        parsed = json.loads(_strip_code_fence(content))
    except json.JSONDecodeError:
        parsed = {}

    return {
        "name": _as_str(parsed.get("name")),
        "email": _as_str(parsed.get("email")),
        "phone": _as_str(parsed.get("phone")),
        "location": _as_str(parsed.get("location")),
        "summary": _as_str(parsed.get("summary")),
        "skills": _as_str_list(parsed.get("skills")),
        "experience": _as_entry_list(parsed.get("experience"), ["title", "company", "duration", "description"]),
        "education": _as_entry_list(parsed.get("education"), ["degree", "institution", "year"]),
    }
