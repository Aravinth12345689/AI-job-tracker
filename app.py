from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///applications.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------------------
# DATABASE MODEL
# ---------------------------
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=True)
    date_applied = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(50), nullable=False, default="Applied")  # Applied, Interview, Offer, Rejected
    notes = db.Column(db.Text, nullable=True)
    job_link = db.Column(db.String(500), nullable=True)
    match_score = db.Column(db.Integer, nullable=True)
    matched_skills = db.Column(db.Text, nullable=True)   # stored as comma-separated
    missing_skills = db.Column(db.Text, nullable=True)   # stored as comma-separated

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "role": self.role,
            "job_description": self.job_description,
            "date_applied": self.date_applied.strftime("%Y-%m-%d"),
            "status": self.status,
            "notes": self.notes,
            "job_link": self.job_link,
            "match_score": self.match_score,
            "matched_skills": self.matched_skills.split(",") if self.matched_skills else [],
            "missing_skills": self.missing_skills.split(",") if self.missing_skills else [],
        }


# Simple single-user resume storage (kept in a text file for this student project)
RESUME_FILE = "resume.txt"

def get_resume_text():
    if os.path.exists(RESUME_FILE):
        with open(RESUME_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_resume_text(text):
    with open(RESUME_FILE, "w", encoding="utf-8") as f:
        f.write(text)


# ---------------------------
# PAGE ROUTES
# ---------------------------
@app.route("/")
def dashboard():
    status_filter = request.args.get("status", "All")
    if status_filter == "All":
        apps = Application.query.order_by(Application.date_applied.desc()).all()
    else:
        apps = Application.query.filter_by(status=status_filter).order_by(Application.date_applied.desc()).all()

    total = Application.query.count()
    interviews = Application.query.filter_by(status="Interview").count()
    offers = Application.query.filter_by(status="Offer").count()
    rejected = Application.query.filter_by(status="Rejected").count()

    stats = {
        "total": total,
        "interviews": interviews,
        "offers": offers,
        "rejected": rejected,
        "interview_rate": round((interviews / total * 100), 1) if total > 0 else 0
    }

    return render_template("dashboard.html", applications=apps, stats=stats, current_filter=status_filter)


@app.route("/add", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":
        new_app = Application(
            company=request.form["company"],
            role=request.form["role"],
            job_description=request.form.get("job_description", ""),
            date_applied=datetime.strptime(request.form["date_applied"], "%Y-%m-%d").date(),
            status=request.form.get("status", "Applied"),
            notes=request.form.get("notes", ""),
            job_link=request.form.get("job_link", "")
        )
        db.session.add(new_app)
        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("add_application.html")


@app.route("/application/<int:app_id>")
def application_detail(app_id):
    application = Application.query.get_or_404(app_id)
    return render_template("application_detail.html", app=application, resume=get_resume_text())


@app.route("/application/<int:app_id>/update_status", methods=["POST"])
def update_status(app_id):
    application = Application.query.get_or_404(app_id)
    application.status = request.form["status"]
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/application/<int:app_id>/delete", methods=["POST"])
def delete_application(app_id):
    application = Application.query.get_or_404(app_id)
    db.session.delete(application)
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/clear-all", methods=["POST"])
def clear_all_applications():
    Application.query.delete()
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/resume", methods=["GET", "POST"])
def resume_page():
    if request.method == "POST":
        save_resume_text(request.form["resume_text"])
        return redirect(url_for("resume_page"))
    return render_template("resume.html", resume=get_resume_text())


# ---------------------------
# AI FEATURE ROUTES (API endpoints)
# ---------------------------
@app.route("/api/match-score/<int:app_id>", methods=["POST"])
def match_score(app_id):
    """
    Calls the AI model to score how well the resume matches the job description.
    """
    from ai_helper import get_match_score

    application = Application.query.get_or_404(app_id)
    resume_text = get_resume_text()

    if not resume_text.strip():
        return jsonify({"error": "Please add your resume text first on the Resume page."}), 400
    if not application.job_description or not application.job_description.strip():
        return jsonify({"error": "This application has no job description saved."}), 400

    result = get_match_score(resume_text, application.job_description)

    if "error" in result:
        return jsonify(result), 500

    application.match_score = result.get("match_score")
    application.matched_skills = ",".join(result.get("matched_skills", []))
    application.missing_skills = ",".join(result.get("missing_skills", []))
    db.session.commit()

    return jsonify(result)


@app.route("/api/generate-email/<int:app_id>", methods=["POST"])
def generate_email(app_id):
    """
    Calls the AI model to draft a polite follow-up email.
    """
    from ai_helper import get_followup_email

    application = Application.query.get_or_404(app_id)
    days_since = (date.today() - application.date_applied).days

    result = get_followup_email(application.company, application.role, days_since)

    if "error" in result:
        return jsonify(result), 500

    return jsonify(result)


# ---------------------------
# APP ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
