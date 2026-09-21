"""
ai_helper.py
------------
This file handles all calls to the AI (LLM) API.

Setup (FREE - Groq API):
1. Get a free API key from https://console.groq.com (no credit card needed)
2. Set it as an environment variable (permanently, via Windows Environment Variables):
       Name:  GROQ_API_KEY
       Value: your key (starts with gsk_...)
3. Install the SDK: pip install groq

Groq's free tier gives 14,400 requests/day on the model used here - far more
than enough for a student project demo.

If you don't have an API key yet, the functions below will return a
clearly-labeled MOCK response so you can still demo the rest of your app
while you wait for API access.
"""

import os
import json
import re

USE_MOCK = os.environ.get("GROQ_API_KEY") is None

if USE_MOCK:
    print("WARNING: GROQ_API_KEY not found in environment - using MOCK responses.")
else:
    key_preview = os.environ.get("GROQ_API_KEY", "")[:8]
    print(f"GROQ_API_KEY found (starts with {key_preview}...) - using REAL AI calls.")


def _call_groq(prompt, max_tokens=500):
    """Low-level helper that calls the free Groq API and returns raw text."""
    from groq import Groq
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    max_tokens=max(max_tokens, 2048),
    messages=[{"role": "user", "content": prompt}]
)
    return response.choices[0].message.content


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
            "suggestions": "[MOCK RESPONSE - set the GROQ_API_KEY environment variable to get real, "
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
        raw = _call_groq(prompt, max_tokens=600)
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
            "body": (f"[MOCK RESPONSE - set the GROQ_API_KEY environment variable for a real AI-generated email]\n\n"
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
        raw = _call_groq(prompt, max_tokens=400)
        return _extract_json(raw)
    except Exception as e:
        return {"error": f"AI call failed: {str(e)}"}
