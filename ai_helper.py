"""
ai_helper.py
------------
This file handles all calls to the AI (LLM) API.

Setup (FREE - Google Gemini API):
1. Get a free API key from https://aistudio.google.com (no credit card needed)
2. Set it as an environment variable before running the app:
       export GEMINI_API_KEY="your-key-here"        (Mac/Linux)
       $env:GEMINI_API_KEY="your-key-here"          (Windows PowerShell)
3. Install the SDK: pip install google-genai

If you don't have an API key yet, the functions below will return a
clearly-labeled MOCK response so you can still demo the rest of your app
while you wait for API access.
"""

import os
import json
import re

USE_MOCK = os.environ.get("GEMINI_API_KEY") is None

# --- DEBUG: prints to your terminal when the app starts, so we can see what's happening ---
if USE_MOCK:
    print("⚠️  GEMINI_API_KEY not found in environment — using MOCK responses.")
else:
    key_preview = os.environ.get("GEMINI_API_KEY", "")[:8]
    print(f"✅ GEMINI_API_KEY found (starts with '{key_preview}...') — using REAL AI calls.")


def _call_gemini(prompt, max_tokens=500):
    """Low-level helper that calls the free Gemini API and returns raw text.
    Retries automatically if Google's servers are temporarily overloaded (503)."""
    import time
    from google import genai
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    last_error = None
    for attempt in range(4):  # try up to 4 times
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            return response.text
        except Exception as e:
            last_error = e
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                time.sleep(2 * (attempt + 1))  # wait longer each retry: 2s, 4s, 6s, 8s
                continue
            raise  # some other error, don't retry, fail immediately

    raise last_error


def _extract_json(text):
    """AI models sometimes wrap JSON in markdown fences - strip those before parsing."""
    cleaned = re.sub(r"```json|```", "", text).strip()
    return json.loads(cleaned)


def get_match_score(resume_text, job_description):
    """
    Returns a dict like:
    {
        "match_score": 78,
        "matched_skills": ["Python", "SQL"],
        "missing_skills": ["Docker", "AWS"],
        "suggestions": "Consider highlighting your database project more clearly."
    }
    """
    if USE_MOCK:
        return {
            "match_score": 72,
            "matched_skills": ["Python", "Communication", "Problem Solving"],
            "missing_skills": ["Docker", "AWS"],
            "suggestions": "[MOCK RESPONSE - set the GEMINI_API_KEY environment variable to get real, "
                            "varying results based on your actual resume and job description] "
                            "Consider adding cloud deployment experience to your resume.",
            "mock": True
        }

    prompt = f"""You are a resume screening assistant. Compare the resume and job description below.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Respond ONLY with a valid JSON object (no other text, no markdown fences) in exactly this format:
{{
  "match_score": <integer 0-100>,
  "matched_skills": [<list of skills/keywords found in both>],
  "missing_skills": [<list of important skills in the JD but missing from resume>],
  "suggestions": "<one short paragraph of specific advice to improve the match>"
}}
"""

    try:
        raw = _call_gemini(prompt, max_tokens=600)
        return _extract_json(raw)
    except Exception as e:
        return {"error": f"AI call failed: {str(e)}"}


def get_followup_email(company, role, days_since_applied):
    """
    Returns a dict like:
    {
        "subject": "Following up on my application - Software Engineer",
        "body": "Dear Hiring Manager, ..."
    }
    """
    if USE_MOCK:
        return {
            "subject": f"Following up on my application - {role}",
            "body": (f"[MOCK RESPONSE - set the GEMINI_API_KEY environment variable for a real AI-generated email]\n\n"
                     f"Dear Hiring Manager,\n\nI hope this message finds you well. I applied for the {role} "
                     f"position at {company} {days_since_applied} days ago and wanted to follow up on my application "
                     f"status. I remain very interested in this opportunity and would welcome the chance to discuss "
                     f"how my skills align with your team's needs.\n\nThank you for your time and consideration.\n\n"
                     f"Best regards,\n[Your Name]"),
            "mock": True
        }

    prompt = f"""Write a short, polite, professional follow-up email for a job application.

Company: {company}
Role: {role}
Days since applied: {days_since_applied}

Respond ONLY with a valid JSON object (no other text, no markdown fences) in exactly this format:
{{
  "subject": "<email subject line>",
  "body": "<email body, 3-4 short paragraphs, polite and professional tone>"
}}
"""

    try:
        raw = _call_gemini(prompt, max_tokens=400)
        return _extract_json(raw)
    except Exception as e:
        return {"error": f"AI call failed: {str(e)}"}
