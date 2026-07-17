# utils/exam_parser.py

import pdfplumber
import docx
import re
from jobapp.models import Job, ExamQuestion, ExamOption


# ===============================
# COMMON PARSER
# ===============================
def parse_questions(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    questions = []
    current_q = None

    for line in lines:

        # -------------------------
        # QUESTION LINE
        # Example: 1. What is Python?
        # -------------------------
        if re.match(r"^\d+\.", line):
            if current_q:
                questions.append(current_q)

            current_q = {
                "question": line.split(".", 1)[1].strip(),
                "options": [],
                "answer": ""
            }

        # -------------------------
        # OPTION LINE
        # Example: A) Text OR A. Text
        # -------------------------
        elif re.match(r"^[A-Da-d][\).]", line):
            if current_q:
                option = re.sub(r"^[A-Da-d][\).]\s*", "", line)
                current_q["options"].append(option.strip())

        # -------------------------
        # ANSWER LINE
        # Example: Answer: B
        # Fix: Extract ONLY the letter after ":" or "-"
        # -------------------------
        elif re.match(r"(?i)^answer\s*[:\-]\s*[A-Da-d]", line):
            if current_q:
                match = re.search(r"[:\-]\s*([A-Da-d])", line)
                if match:
                    current_q["answer"] = match.group(1).upper()

    if current_q:
        questions.append(current_q)

    return questions


# ===============================
# PDF EXTRACT
# ===============================
def extract_questions_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return parse_questions(text)


# ===============================
# DOCX EXTRACT
# ===============================
def extract_questions_from_docx(path):
    doc = docx.Document(path)
    text = "\n".join(p.text for p in doc.paragraphs)
    return parse_questions(text)


# ===============================
# CREATE QUESTIONS IN DB
# ===============================
def create_exam_questions(job: Job, questions_data: list):

    # Delete old questions for this job
    ExamQuestion.objects.filter(job=job).delete()

    for q_data in questions_data:
        question_text = q_data.get("question", "").strip()
        if not question_text:
            continue

        question = ExamQuestion.objects.create(
            job=job,
            text=question_text
        )

        answer = q_data.get("answer", "").upper()

        for idx, option_text in enumerate(q_data.get("options", [])):
            option_letter = chr(65 + idx)  # A, B, C, D

            ExamOption.objects.create(
                question=question,
                text=option_text.strip(),
                is_correct=(option_letter == answer)
            )


# ===============================
# AUTO GENERATE (fallback)
# ===============================
def auto_generate_questions(title, skills):
    return [
        {
            "question": f"What is {skills}?",
            "options": [
                "Programming Language",
                "Database",
                "Protocol",
                "Hardware"
            ],
            "answer": "A"
        },
        {
            "question": f"{title} mainly works on?",
            "options": [
                "Frontend",
                "Backend",
                "Networking",
                "Design"
            ],
            "answer": "B"
        }
    ]