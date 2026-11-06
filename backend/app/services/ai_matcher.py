import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

PROMPT = """You are a technical recruiter. Compare the resume with the job description.
Return ONLY JSON with exactly this shape:
{
  "required_skills": ["skills the job asks for"],
  "matched_skills": ["required skills the resume clearly shows"],
  "missing_skills": ["required skills the resume does not show"],
  "match_score": 0,
  "suggestions": ["specific, honest ways to improve the resume for this job"]
}
match_score is an integer from 0 to 100. Use only the text provided. Never invent
skills or experience the resume does not mention.

JOB DESCRIPTION:
<<JD>>

RESUME:
<<RESUME>>
"""

MAX_ATTEMPTS = 3


def analyze_match(job_description: str, resume_text: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)
    prompt = PROMPT.replace("<<JD>>", job_description).replace("<<RESUME>>", resume_text)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            return json.loads(response.text)
        except errors.ServerError:
            # Google is busy (503 etc.). Wait a little, then try again.
            if attempt == MAX_ATTEMPTS:
                raise
            time.sleep(2 * attempt)