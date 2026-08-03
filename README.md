# AI Job Application Tracker

A final-year project: track job applications and get AI-powered resume-match
scoring and follow-up email drafts.

## Features
- Add / view / update / delete job applications
- Dashboard with stats (total applied, interviews, offers, interview rate)
- Filter applications by status
- **AI Resume Match Score** — paste your resume once, then get a match score
  + missing skills for any job description you save
- **AI Follow-up Email Generator** — auto-drafts a polite follow-up email
  based on company, role, and days since applying

## Project structure
```
job_tracker/
├── app.py              # Flask app: routes, database models
├── ai_helper.py         # All AI (LLM) API calls live here
├── requirements.txt
├── templates/           # HTML pages (Jinja2)
│   ├── base.html
│   ├── dashboard.html
│   ├── add_application.html
│   ├── application_detail.html
│   └── resume.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## How to run it

1. **Install Python 3.10+** if you don't have it already.

2. **Install dependencies:**
   ```bash
   cd job_tracker
   pip install -r requirements.txt
   ```

3. **(Optional but recommended) Add your AI API key**
   Without this, the AI features still work but return clearly-labeled
   MOCK data so you can still demo the rest of the app.

   Get a key from https://console.anthropic.com, then run:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"      # Mac/Linux
   set ANTHROPIC_API_KEY=your-key-here            # Windows cmd
   ```

4. **Run the app:**
   ```bash
   python app.py
   ```

5. Open your browser to **http://localhost:5000**

The database (`applications.db`) is created automatically on first run.

## For your project report

- **Problem it solves:** job seekers apply to many roles and lose track of
  status, deadlines, and how well their resume actually fits each role.
- **AI component:** an LLM (Claude) is prompted to (1) compare resume text
  against a job description and return a match score + missing skills, and
  (2) draft a personalized follow-up email. This is what distinguishes it
  from a plain CRUD tracker.
- **Limitations to mention in your defense:**
  - Match score is a heuristic guide, not a guarantee of interview success
  - Requires the user to paste resume/JD text manually (no resume file
    parsing or auto-scraping job postings — a good "future scope" point)
  - Single-user design for simplicity (add login/auth as future scope if asked)

## Possible extensions (future scope)
- Multi-user login with authentication
- PDF resume upload + text extraction instead of manual paste
- Auto-fill job details from a pasted job posting URL
- Kanban drag-and-drop board view
- Email reminders (not just on-demand generation)
