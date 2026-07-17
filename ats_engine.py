import re
from pdfminer.high_level import extract_text
from docx import Document

def extract_resume_text(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        text = extract_text(file_path)
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text.lower()

def calculate_ats_score(job_skills, resume_text):
    if not job_skills:
        return 0, [], []

    job_skills = [skill.strip().lower() for skill in job_skills.split(",") if skill.strip()]
    matched, missing = [], []
    for skill in job_skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, resume_text):
            matched.append(skill)
        else:
            missing.append(skill)

    score = int((len(matched) / len(job_skills)) * 100) if job_skills else 0
    return score, matched, missing
