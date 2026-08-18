import os
import json
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from extensions import db

from models import (
    User,
    Job,
    Candidate,
    Resume,
    Ranking,
    Skill,
    CandidateSkill
)

from services.resume_parser import allowed_file, extract_text
from services.candidate_parser import parse_candidate
from services.nlp_matcher import calculate_match


# ---------------------------------------------------------
# FLASK APP CONFIGURATION
# ---------------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Create upload folder if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# ---------------------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------------------

with app.app_context():
    db.create_all()


# ---------------------------------------------------------
# LOGIN REQUIRED DECORATOR
# ---------------------------------------------------------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def index():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validation
        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        # Check existing user
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered.", "danger")
            return redirect(url_for("register"))

        # Create user
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(
                password,
                method="pbkdf2:sha256"
            )
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):

            session["user_id"] = user.id
            session["user_name"] = user.name

            return redirect(url_for("dashboard"))

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template("login.html")


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    user_id = session["user_id"]

    jobs = (
        Job.query
        .filter_by(user_id=user_id)
        .order_by(Job.created_at.desc())
        .all()
    )

    job_ids = [job.id for job in jobs]

    # Resume count
    if job_ids:
        resume_count = (
            Resume.query
            .filter(Resume.job_id.in_(job_ids))
            .count()
        )
    else:
        resume_count = 0

    # Ranking count
    if job_ids:
        ranking_count = (
            Ranking.query
            .filter(Ranking.job_id.in_(job_ids))
            .count()
        )
    else:
        ranking_count = 0

    # Top candidates
    if job_ids:

        top_rankings = (
            Ranking.query
            .filter(Ranking.job_id.in_(job_ids))
            .order_by(Ranking.overall_score.desc())
            .limit(5)
            .all()
        )

    else:
        top_rankings = []

    return render_template(
        "dashboard.html",
        jobs=jobs,
        resume_count=resume_count,
        ranking_count=ranking_count,
        top_rankings=top_rankings
    )


# ---------------------------------------------------------
# JOB LIST
# ---------------------------------------------------------

@app.route("/jobs")
@login_required
def jobs():

    jobs = (
        Job.query
        .filter_by(user_id=session["user_id"])
        .order_by(Job.created_at.desc())
        .all()
    )

    return render_template(
        "jobs.html",
        jobs=jobs
    )


# ---------------------------------------------------------
# CREATE JOB
# ---------------------------------------------------------

@app.route("/jobs/new", methods=["GET", "POST"])
@login_required
def create_job():

    if request.method == "POST":

        job = Job(
            user_id=session["user_id"],
            title=request.form.get(
                "title",
                ""
            ).strip(),

            description=request.form.get(
                "description",
                ""
            ).strip(),

            required_skills=request.form.get(
                "required_skills",
                ""
            ).strip(),

            education=request.form.get(
                "education",
                ""
            ).strip(),

            experience=request.form.get(
                "experience",
                ""
            ).strip()
        )

        # Required fields
        if not job.title or not job.description:

            flash(
                "Job title and description are required.",
                "danger"
            )

            return redirect(
                url_for("create_job")
            )

        db.session.add(job)
        db.session.commit()

        flash(
            "Job created successfully.",
            "success"
        )

        return redirect(
            url_for("jobs")
        )

    return render_template(
        "job_form.html"
    )


# ---------------------------------------------------------
# JOB DETAIL / RANKING
# ---------------------------------------------------------

@app.route("/jobs/<int:job_id>")
@login_required
def job_detail(job_id):

    job = (
        Job.query
        .filter_by(
            id=job_id,
            user_id=session["user_id"]
        )
        .first_or_404()
    )

    rankings = (
        Ranking.query
        .filter_by(job_id=job.id)
        .order_by(
            Ranking.overall_score.desc()
        )
        .all()
    )

    return render_template(
        "ranking.html",
        job=job,
        rankings=rankings
    )


# ---------------------------------------------------------
# UPLOAD RESUMES
# ---------------------------------------------------------

@app.route(
    "/jobs/<int:job_id>/upload",
    methods=["GET", "POST"]
)
@login_required
def upload_resumes(job_id):

    job = (
        Job.query
        .filter_by(
            id=job_id,
            user_id=session["user_id"]
        )
        .first_or_404()
    )

    if request.method == "POST":

        files = request.files.getlist("resumes")

        if not files:

            flash(
                "Please select at least one resume.",
                "danger"
            )

            return redirect(
                url_for(
                    "upload_resumes",
                    job_id=job.id
                )
            )

        created = 0

        for file in files:

            # Skip empty files
            if not file or not file.filename:
                continue

            # Check file type
            if not allowed_file(file.filename):

                flash(
                    f"Unsupported file: {file.filename}. "
                    "Use PDF or DOCX.",
                    "warning"
                )

                continue

            # Secure filename
            safe_name = secure_filename(
                file.filename
            )

            # Generate unique filename
            unique_name = (
                f"{job.id}_"
                f"{session['user_id']}_"
                f"{os.urandom(6).hex()}_"
                f"{safe_name}"
            )

            path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                unique_name
            )

            # Save uploaded file
            file.save(path)

            # -------------------------------------------------
            # EXTRACT RESUME TEXT
            # -------------------------------------------------

            try:

                text = extract_text(path)

                info = parse_candidate(text)

                # Convert skills list to string
                if isinstance(
                    info.get("skills_text"),
                    list
                ):

                    info["skills_text"] = ", ".join(
                        info["skills_text"]
                    )

            except Exception as exc:

                flash(
                    f"Could not parse "
                    f"{file.filename}: {exc}",
                    "danger"
                )

                continue

            # -------------------------------------------------
            # CREATE CANDIDATE
            # -------------------------------------------------

            candidate = Candidate(**info)

            db.session.add(candidate)

            db.session.flush()

            # -------------------------------------------------
            # CREATE RESUME
            # -------------------------------------------------

            resume = Resume(
                job_id=job.id,
                candidate_id=candidate.id,
                filename=unique_name,
                extracted_text=text
            )

            db.session.add(resume)

            db.session.flush()

            # -------------------------------------------------
            # CALCULATE MATCH
            # -------------------------------------------------

            result = calculate_match(
                job,
                text
            )

            # -------------------------------------------------
            # GET EXPLANATION
            # -------------------------------------------------

            explanation_data = result.get(
                "explanation",
                {
                    "summary": "Explanation not available.",
                    "strengths": [],
                    "improvements": [],
                    "suggestions": []
                }
            )

            # Make sure explanation is JSON
            if isinstance(
                explanation_data,
                dict
            ):

                explanation_json = json.dumps(
                    explanation_data
                )

            else:

                explanation_json = json.dumps(
                    {
                        "summary": str(
                            explanation_data
                        ),
                        "strengths": [],
                        "improvements": [],
                        "suggestions": []
                    }
                )

            # -------------------------------------------------
            # CREATE RANKING
            # -------------------------------------------------

            ranking = Ranking(
                job_id=job.id,
                candidate_id=candidate.id,

                overall_score=result[
                    "overall_score"
                ],

                text_score=result[
                    "text_score"
                ],

                skill_score=result[
                    "skill_score"
                ],

                education_score=result[
                    "education_score"
                ],

                experience_score=result[
                    "experience_score"
                ],

                matched_skills=", ".join(
                    result["matched_skills"]
                ),

                missing_skills=", ".join(
                    result["missing_skills"]
                ),

                explanation=explanation_json
            )

            db.session.add(ranking)

            # -------------------------------------------------
            # SAVE SKILLS
            # -------------------------------------------------

            for skill_name in result[
                "matched_skills"
            ]:

                skill = (
                    Skill.query
                    .filter_by(
                        name=skill_name
                    )
                    .first()
                )

                if not skill:

                    skill = Skill(
                        name=skill_name
                    )

                    db.session.add(skill)

                    db.session.flush()

                candidate_skill = CandidateSkill(
                    candidate_id=candidate.id,
                    skill_id=skill.id
                )

                db.session.add(
                    candidate_skill
                )

            created += 1

        # -----------------------------------------------------
        # COMMIT EVERYTHING
        # -----------------------------------------------------

        db.session.commit()

        flash(
            f"{created} resume(s) processed successfully.",
            "success"
        )

        return redirect(
            url_for(
                "job_detail",
                job_id=job.id
            )
        )

    return render_template(
        "upload.html",
        job=job
    )


# ---------------------------------------------------------
# CANDIDATE DETAIL + EXPLAINABLE AI
# ---------------------------------------------------------

@app.route(
    "/candidates/<int:candidate_id>"
)
@login_required
def candidate_detail(candidate_id):

    # -------------------------------------------------
    # FIND CANDIDATE
    # -------------------------------------------------

    candidate = (
        Candidate.query
        .get_or_404(candidate_id)
    )

    # -------------------------------------------------
    # FIND LATEST RANKING
    # -------------------------------------------------

    ranking = (
        Ranking.query
        .filter_by(
            candidate_id=candidate.id
        )
        .order_by(
            Ranking.created_at.desc()
        )
        .first()
    )

    # Ranking doesn't exist
    if not ranking:

        flash(
            "Ranking not found.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    # -------------------------------------------------
    # FIND JOB
    # -------------------------------------------------

    job = Job.query.get(
        ranking.job_id
    )

    # Security check
    if not job or job.user_id != session["user_id"]:

        flash(
            "Candidate not found.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    # -------------------------------------------------
    # FIND RESUME
    # -------------------------------------------------

    resume = (
        Resume.query
        .filter_by(
            candidate_id=candidate.id,
            job_id=ranking.job_id
        )
        .first()
    )

    # -------------------------------------------------
    # DEFAULT EXPLANATION
    # -------------------------------------------------

    explanation = {
        "summary": "Explanation not available.",
        "strengths": [],
        "improvements": [],
        "suggestions": []
    }

    # -------------------------------------------------
    # LOAD EXPLANATION FROM DATABASE
    # -------------------------------------------------

    if ranking.explanation:

        try:

            explanation = json.loads(
                ranking.explanation
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            explanation = {
                "summary": str(
                    ranking.explanation
                ),
                "strengths": [],
                "improvements": [],
                "suggestions": []
            }

    # -------------------------------------------------
    # RENDER CANDIDATE PAGE
    # -------------------------------------------------

    return render_template(
        "candidate.html",

        candidate=candidate,

        ranking=ranking,

        resume=resume,

        explanation=explanation
    )


# ---------------------------------------------------------
# FILE TOO LARGE
# ---------------------------------------------------------

@app.errorhandler(413)
def too_large(_):

    flash(
        "File is too large. Maximum allowed size is 10 MB.",
        "danger"
    )

    return redirect(
        request.referrer
        or url_for("dashboard")
    )


# ---------------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True,port=5050)