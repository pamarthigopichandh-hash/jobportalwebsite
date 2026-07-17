from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import JobApplication, Job, JobSeekerProfile
from .ats_engine import extract_resume_text, calculate_ats_score
import os


# ==============================
# ATS AUTO SHORTLIST SYSTEM
# ==============================
@receiver(post_save, sender=JobApplication)
def run_ats(sender, instance, created, **kwargs):

    if not created:
        return

    try:
        resume_path = instance.resume.path

        if not os.path.exists(resume_path):
            return

        resume_text = extract_resume_text(resume_path)

        score, matched, missing = calculate_ats_score(
            instance.job.skills_required,
            resume_text
        )

        # ===== AUTO DECISION =====
        if score >= 70:
            status = "Accepted"
            is_auto = True
            subject = "🎉 Application Auto Accepted"
            message = f"""
Hello {instance.full_name},

Congratulations!

Your application for "{instance.job.title}" at {instance.job.company}
has been automatically ACCEPTED based on your ATS score: {score}%

HR team will contact you soon.

Best Regards,
{instance.job.company}
"""

        elif score < 30:
            status = "Rejected"
            is_auto = False
            subject = "Application Update"
            message = f"""
Hello {instance.full_name},

Thank you for applying for "{instance.job.title}" at {instance.job.company}.

Unfortunately, your profile does not match the requirements.

We encourage you to apply again after improving skills.

Best Regards,
{instance.job.company}
"""

        else:
            status = "Pending"
            is_auto = False
            subject = None

        # 🔥 SAFE UPDATE (NO LOOP)
        JobApplication.objects.filter(id=instance.id).update(
            ats_score=score,
            matched_skills=", ".join(matched),
            missing_skills=", ".join(missing),
            status=status,
            is_auto_shortlisted=is_auto,
            ats_processed=True
        )

        # Send email only for accept/reject
        if subject and instance.email:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=True
            )

    except Exception as e:
        print("ATS ERROR:", e)


# ==========================================
# 🔔 SKILL MATCH JOB ALERT SYSTEM (NEW)
# ==========================================
@receiver(post_save, sender=Job)
def send_skill_match_alert(sender, instance, created, **kwargs):

    if not created:
        return

    if not instance.skills_required:
        return

    try:
        job_skills = [
            skill.strip().lower()
            for skill in instance.skills_required.split(",")
            if skill.strip()
        ]

        jobseekers = JobSeekerProfile.objects.all()

        for seeker in jobseekers:

            if not seeker.skills:
                continue

            seeker_skills = [
                skill.strip().lower()
                for skill in seeker.skills.split(",")
                if skill.strip()
            ]

            # Find matching skills
            matched = set(job_skills) & set(seeker_skills)

            if matched and seeker.user.email:

                subject = "🚀 New Job Posted That Matches Your Skills!"

                message = f"""
Hello {seeker.user.username},

Good news!

A new job "{instance.title}" at {instance.company}
has been posted that matches your skills.

Matched Skills: {', '.join(matched)}

Login to your dashboard and apply now.

Best Regards,
Job Portal Team
"""

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [seeker.user.email],
                    fail_silently=True
                )

    except Exception as e:
        print("Skill Match Alert Error:", e)
        
        
        
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Job, ExamQuestion, ExamOption
from PyPDF2 import PdfReader
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Job, ExamQuestion, ExamOption
from PyPDF2 import PdfReader
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Job, ExamQuestion, ExamOption
from PyPDF2 import PdfReader
import os
# jobapp/signals.py
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from PyPDF2 import PdfReader
from .models import Job, ExamQuestion, ExamOption

@receiver(post_save, sender=Job)
def import_exam_pdf(sender, instance, created, **kwargs):
    if not instance.exam_file:
        return

    pdf_path = instance.exam_file.path
    if not os.path.exists(pdf_path):
        print("❌ PDF file does not exist:", pdf_path)
        return

    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        # Split questions (Q1, Q2, or just Q)
        questions = [q.strip() for q in text.split("Q") if q.strip()]

        for q_text in questions:
            lines = [line.strip() for line in q_text.split("\n") if line.strip()]
            if len(lines) < 2:
                continue

            # QUESTION
            question_line = lines[0]
            question_text = question_line.split(":", 1)[-1].strip() if ":" in question_line else question_line
            q = ExamQuestion.objects.create(job=instance, text=question_text)

            options = []
            correct_index = None
            for line in lines[1:]:
                line_clean = line.replace(" ", "").lower()
                if line_clean.startswith("answer:"):
                    letter = line_clean.split(":")[-1]
                    if letter in ["a", "b", "c", "d"]:
                        correct_index = ord(letter) - ord("a")
                elif line and line[0].lower() in ["a", "b", "c", "d"] and ")" in line:
                    opt_text = line.split(")", 1)[-1].strip()
                    options.append(opt_text)

            for i, opt_text in enumerate(options):
                is_correct = (i == correct_index)
                ExamOption.objects.create(question=q, text=opt_text, is_correct=is_correct)

        print(f"✅ Imported {len(questions)} questions from PDF successfully!")

    except Exception as e:
        print("❌ PDF import error:", e)
        
        
        
        
      
# -----------------------------------------------------create_profile--------------------  
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import EmployerProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

    if created and instance.role == "employer":
        EmployerProfile.objects.create(user=instance)
        

# ----------------------------create_employer_user_profile-----------------------------

from .models import EmployerUserProfile


User = get_user_model()


@receiver(post_save, sender=User)
def create_employer_user_profile(sender, instance, created, **kwargs):
    if created:
        EmployerUserProfile.objects.create(user=instance)