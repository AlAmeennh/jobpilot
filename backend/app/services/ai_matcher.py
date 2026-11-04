import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

# Model names change over time. If this one stops working, check Google AI Studio
# for a current name and set GEMINI_MODEL in .env.
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

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


def analyze_match(job_description: str, resume_text: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)
    prompt = PROMPT.replace("<<JD>>", job_description).replace("<<RESUME>>", resume_text)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    return json.loads(response.text)