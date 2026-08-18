from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import re

import PyPDF2
from docx import Document


# =====================================================
# FLASK APP
# =====================================================

app = Flask(__name__)

# =====================================================
# CONFIGURATION
# =====================================================

UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {"pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =====================================================
# CHECK FILE
# =====================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =====================================================
# PDF TEXT
# =====================================================

def extract_pdf_text(filepath):

    text = ""

    try:

        with open(filepath, "rb") as file:

            reader = PyPDF2.PdfReader(file)

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    except Exception as e:

        print("PDF ERROR:", e)

    return text


# =====================================================
# DOCX TEXT
# =====================================================

def extract_docx_text(filepath):

    text = ""

    try:

        document = Document(filepath)

        for paragraph in document.paragraphs:

            text += paragraph.text + "\n"

    except Exception as e:

        print("DOCX ERROR:", e)

    return text


# =====================================================
# RESUME TEXT
# =====================================================

def extract_resume_text(filepath):

    extension = filepath.rsplit(".", 1)[1].lower()

    if extension == "pdf":

        return extract_pdf_text(filepath)

    elif extension == "docx":

        return extract_docx_text(filepath)

    return ""


# =====================================================
# SKILLS
# =====================================================

SKILLS = [

    "Python",
    "Java",
    "C++",
    "JavaScript",
    "HTML",
    "CSS",

    "React",
    "Angular",
    "Vue",

    "Node.js",
    "Express.js",

    "Spring Boot",
    "Django",
    "Flask",

    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",

    "Git",
    "GitHub",

    "Docker",
    "Kubernetes",

    "AWS",
    "Azure",
    "Google Cloud",

    "Machine Learning",
    "Deep Learning",

    "TensorFlow",
    "PyTorch",

    "Pandas",
    "NumPy",

    "Power BI",
    "Excel",

    "REST API",
    "API",

    "Data Structures",
    "Algorithms",

    "Hibernate",
    "Statistics"
]


# =====================================================
# JOB ROLE SKILLS
# =====================================================

ROLE_SKILLS = {

    "java developer": [
        "Java",
        "Spring Boot",
        "MySQL",
        "Git",
        "REST API",
        "Hibernate",
        "SQL",
        "Docker"
    ],

    "python developer": [
        "Python",
        "Django",
        "Flask",
        "SQL",
        "Git",
        "REST API",
        "Pandas",
        "NumPy"
    ],

    "frontend developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Git",
        "REST API"
    ],

    "backend developer": [
        "Java",
        "Python",
        "Node.js",
        "SQL",
        "MongoDB",
        "REST API",
        "Git",
        "Docker"
    ],

    "data scientist": [
        "Python",
        "Pandas",
        "NumPy",
        "Machine Learning",
        "SQL",
        "TensorFlow",
        "Statistics"
    ],

    "data analyst": [
        "Python",
        "SQL",
        "Excel",
        "Power BI",
        "Pandas",
        "Statistics"
    ],

    "full stack developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Node.js",
        "MongoDB",
        "SQL",
        "Git"
    ]
}


# =====================================================
# FIND SKILLS
# =====================================================

def find_skills(text):

    text_lower = text.lower()

    found = []

    for skill in SKILLS:

        if skill.lower() in text_lower:

            found.append(skill)

    return found


# =====================================================
# REQUIRED SKILLS
# =====================================================

def get_required_skills(job_role):

    role = job_role.lower().strip()

    for key, skills in ROLE_SKILLS.items():

        if key in role:

            return skills

    return [
        "Python",
        "Java",
        "JavaScript",
        "SQL",
        "Git",
        "HTML",
        "CSS"
    ]


# =====================================================
# KEYWORD SCORE
# =====================================================

def calculate_keyword_score(found, required):

    if not required:

        return 0

    matched = 0

    for skill in required:

        if skill in found:

            matched += 1

    return round(
        (matched / len(required)) * 100
    )


# =====================================================
# STRUCTURE SCORE
# =====================================================

def calculate_structure_score(text):

    text = text.lower()

    sections = [
        "experience",
        "education",
        "skills",
        "projects",
        "summary"
    ]

    found = 0

    for section in sections:

        if section in text:

            found += 1

    return round(
        (found / len(sections)) * 100
    )


# =====================================================
# FORMAT SCORE
# =====================================================

def calculate_format_score(text):

    score = 100

    if len(text.strip()) < 500:

        score -= 20

    if len(text.strip()) < 200:

        score -= 20

    if not re.search(
        r"[\w\.-]+@[\w\.-]+\.\w+",
        text
    ):

        score -= 10

    if not re.search(
        r"\b\d{10}\b",
        text
    ):

        score -= 10

    return max(0, score)


# =====================================================
# ATS SCORE
# =====================================================

def calculate_ats_score(
    keyword,
    structure,
    formatting
):

    score = (

        keyword * 0.60

        + structure * 0.25

        + formatting * 0.15

    )

    return round(score)


# =====================================================
# SUGGESTIONS
# =====================================================

def generate_suggestions(
    missing,
    keyword,
    structure,
    formatting
):

    suggestions = []

    if missing:

        suggestions.append(
            "Relevant missing keywords: "
            + ", ".join(missing[:5])
            + ". Add them only if you actually "
              "have these skills."
        )

    if keyword < 70:

        suggestions.append(
            "Improve keyword matching according "
            "to the target job role."
        )

    if structure < 80:

        suggestions.append(
            "Add clear sections such as Summary, "
            "Skills, Experience, Education and Projects."
        )

    if formatting < 80:

        suggestions.append(
            "Improve resume formatting so ATS can "
            "read the information easily."
        )

    suggestions.append(
        "Add measurable achievements using "
        "numbers and percentages where appropriate."
    )

    return suggestions


# =====================================================
# HOME PAGE
# =====================================================

@app.route("/")
def home():

    return render_template("index.html")


# =====================================================
# ANALYZE API
# =====================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        # ---------------------------------------------
        # FILE
        # ---------------------------------------------

        if "resume" not in request.files:

            return jsonify({
                "success": False,
                "error": "Please upload your resume."
            }), 400

        file = request.files["resume"]

        if file.filename == "":

            return jsonify({
                "success": False,
                "error": "No file selected."
            }), 400

        if not allowed_file(file.filename):

            return jsonify({
                "success": False,
                "error": "Only PDF and DOCX files are allowed."
            }), 400


        # ---------------------------------------------
        # JOB ROLE
        # ---------------------------------------------

        job_role = request.form.get(
            "jobRole",
            ""
        ).strip()

        if not job_role:

            return jsonify({
                "success": False,
                "error": "Please enter target job role."
            }), 400


        # ---------------------------------------------
        # SAVE FILE
        # ---------------------------------------------

        filename = secure_filename(
            file.filename
        )

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)


        # ---------------------------------------------
        # EXTRACT TEXT
        # ---------------------------------------------

        resume_text = extract_resume_text(
            filepath
        )

        if not resume_text.strip():

            return jsonify({
                "success": False,
                "error": (
                    "Could not read the resume. "
                    "Make sure your PDF contains selectable text."
                )
            }), 400


        # ---------------------------------------------
        # FIND SKILLS
        # ---------------------------------------------

        found_skills = find_skills(
            resume_text
        )


        # ---------------------------------------------
        # REQUIRED SKILLS
        # ---------------------------------------------

        required_skills = get_required_skills(
            job_role
        )


        # ---------------------------------------------
        # MISSING SKILLS
        # ---------------------------------------------

        missing_skills = [

            skill

            for skill in required_skills

            if skill not in found_skills

        ]


        # ---------------------------------------------
        # CALCULATE SCORES
        # ---------------------------------------------

        keyword_score = calculate_keyword_score(
            found_skills,
            required_skills
        )

        structure_score = calculate_structure_score(
            resume_text
        )

        format_score = calculate_format_score(
            resume_text
        )

        ats_score = calculate_ats_score(
            keyword_score,
            structure_score,
            format_score
        )


        # ---------------------------------------------
        # GRADE
        # ---------------------------------------------

        if ats_score >= 90:

            grade = "A+"
            title = "Excellent ATS Compatibility"

        elif ats_score >= 80:

            grade = "A"
            title = "Very Good ATS Compatibility"

        elif ats_score >= 70:

            grade = "B"
            title = "Good ATS Compatibility"

        elif ats_score >= 60:

            grade = "C"
            title = "Average ATS Compatibility"

        else:

            grade = "D"
            title = "Needs Improvement"


        # ---------------------------------------------
        # SUGGESTIONS
        # ---------------------------------------------

        suggestions = generate_suggestions(
            missing_skills,
            keyword_score,
            structure_score,
            format_score
        )


        # ---------------------------------------------
        # RETURN JSON
        # ---------------------------------------------

        return jsonify({

            "success": True,

            "score": ats_score,

            "grade": grade,

            "title": title,

            "jobRole": job_role,

            "foundSkills": found_skills,

            "missingSkills": missing_skills,

            "keywordScore": keyword_score,

            "structureScore": structure_score,

            "formatScore": format_score,

            "suggestions": suggestions

        })


    except Exception as e:

        print("ERROR:", e)

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )