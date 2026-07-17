from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils.text import slugify
# Create your models here.


class User(AbstractUser):
    ROLE_CHOICES = (
        ('jobseeker', 'Job Seeker'),
        ('employer', 'Employer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


# from django.conf import settings

# class Profile(models.Model):
    
# user = models.OneToOneField(User, on_delete=models.CASCADE)

from django.conf import settings   



# ===============================
# JOB SEEKER PROFILE
# ===============================
class JobSeekerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    profile_photo = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    headline = models.CharField(max_length=255,blank=True,null=True)
    full_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)

    gender = models.CharField(max_length=20)

    qualification = models.CharField(max_length=200)
    skills = models.TextField(max_length=200)

    address = models.TextField( max_length=500)
    about = models.TextField(max_length=500)

    resume = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


# ===============================
# EXPERIENCE
# ===============================
class Experience(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    description = models.TextField()

    def __str__(self):
        return self.role


# ===============================
# EDUCATION
# ===============================
class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    year = models.CharField(max_length=20)

    def __str__(self):
        return self.degree
    
    
    
# ---------------------------------Company------------------------------------
class Company(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# ---------------------------------JOB------------------------------------


from django.conf import settings
from django.db import models



class Job(models.Model):

    # ================= EMPLOYER =================
    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'employer'}
    )

    company = models.CharField(max_length=200)
    
    # ================= BASIC =================
    title = models.CharField(max_length=150)

    location = models.CharField(max_length=150)

    description = models.TextField()

    salary = models.CharField(max_length=100)

    # ================= ATS =================
    skills_required = models.TextField(
        help_text="python, django, sql",
        blank=True,
        null=True
    )

    exam_file = models.FileField(
        upload_to="exams/",
        blank=True,
        null=True
    )

    # ================= FILTER SYSTEM =================

    CATEGORY_CHOICES = [
        ('IT', 'IT'),
        ('NON-IT', 'NON-IT'),
    ]

    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Internship', 'Internship'),
    ]

    WORK_MODE = [
        ('Office', 'Work from office'),
        ('Hybrid', 'Hybrid'),
        ('Remote', 'Remote'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)

    work_mode = models.CharField(
        max_length=20,
        choices=WORK_MODE,
        default="Office"
    )

    department = models.CharField(max_length=150, blank=True)

    role_category = models.CharField(max_length=150, blank=True)

    stipend = models.IntegerField(null=True, blank=True)

    duration = models.CharField(max_length=50, blank=True)

    # ================= META =================
    deadline = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
# ---------------------------------JobApplication------------------------------------

# ==========================================================
# JOB APPLICATION MODEL
# ==========================================================
class JobApplication(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Viewed", "Viewed"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
        ("Shortlisted", "Shortlisted"),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "jobseeker"}
    )

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to="resumes/")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    # ===== ATS TRACKING FIELDS =====
    ats_score = models.IntegerField(default=0)
    matched_skills = models.TextField(blank=True)
    missing_skills = models.TextField(blank=True)
    is_auto_shortlisted = models.BooleanField(default=False)
    ats_processed = models.BooleanField(default=False)

    # ===== EXAMINATION FIELDS =====
    exam_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,          # ensures each application has a unique exam link
        null=False,
        blank=False
    )
    exam_completed = models.BooleanField(default=False)  # always starts as False
    exam_score = models.IntegerField(null=True, blank=True)
    final_score = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("job", "user")  # Prevent duplicate applications
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.full_name} applied for {self.job.title}"


#---------------------------------------EMAIL_APPLICATION_----------------------------------
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    exam_score = models.IntegerField(default=0)
    exam_completed = models.BooleanField(default=False)
#-------------------------------------------user_APPLICATION--------------------------------
class User_Application(models.Model):

    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied'
    )

    applied_at = models.DateTimeField(auto_now_add=True)
class DecisionLog(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE)
    employer = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20)  # Accepted, Rejected, Viewed, Withdrawn
    ats_score = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.conf import settings

# ---------------------------------Exam Question Bank------------------------------------
import uuid
from django.db import models
from django.conf import settings

# ---------------------------------Exam Question Bank------------------------------------
class ExamQuestion(models.Model):
    job = models.ForeignKey("Job", on_delete=models.CASCADE, related_name="exam_questions")
    text = models.TextField()
    correct_option_index = models.IntegerField(null=True, blank=True)  

    def __str__(self):
        return f"{self.job.title} - {self.text[:50]}..."


class ExamOption(models.Model):
    question = models.ForeignKey("ExamQuestion", on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Option for {self.question.text[:30]}... ({'Correct' if self.is_correct else 'Wrong'})"




# ---------------------------------Exam Attempt------------------------------------
class ExamAttempt(models.Model):
    application = models.ForeignKey("JobApplication", on_delete=models.CASCADE, related_name="exam_attempts")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Passed", "Passed"), ("Failed", "Failed")],
        default="Pending"
    )

    def __str__(self):
        return f"{self.application.user.username} - {self.application.job.title} ({self.status})"


# ---------------------------------Exam Result------------------------------------
class ExamResult(models.Model):
    application = models.OneToOneField("JobApplication", on_delete=models.CASCADE, related_name="exam_result")
    exam = models.ForeignKey("Job", on_delete=models.CASCADE, related_name="exam_results")
    score = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Shortlisted", "Shortlisted"), ("Rejected", "Rejected")],
        default="Pending"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application.user.username} - {self.exam.title} ({self.status})"

class ExamAnswer(models.Model):
    attempt = models.ForeignKey("ExamAttempt", on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey("ExamQuestion", on_delete=models.CASCADE)
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attempt.application.user.username} - {self.question.text[:50]}..."
    
# ---------# --------------------EmployerProfile---------------------------------------------------
import os
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from PIL import Image

class EmployerProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    company_name = models.CharField(max_length=200)

    logo = models.ImageField(
        upload_to="company_logos/",
        blank=True,
        null=True
    )

    cover_image = models.ImageField(
        upload_to="cover_images/",
        blank=True,
        null=True
    )

    tagline = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)

    industry = models.CharField(max_length=150, blank=True)
    company_size = models.CharField(max_length=100, blank=True)

    founded_year = models.IntegerField(null=True, blank=True)

    website = models.URLField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)

    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    facebook = models.URLField(blank=True)

    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.company_name)

        super().save(*args, **kwargs)

    #    Safe image resize
        if self.logo and os.path.exists(self.logo.path):
            img = Image.open(self.logo.path)
            img.thumbnail((400, 400))
            img.save(self.logo.path)

        if self.cover_image and os.path.exists(self.cover_image.path):
            img = Image.open(self.cover_image.path)
            img.thumbnail((1400, 600))
            img.save(self.cover_image.path)

    def __str__(self):
        return self.company_name
# --------------------EmployerUserProfile----------------------------

class EmployerUserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    profile_pic = models.ImageField(
        upload_to="employer_profile/",
        blank=True,
        null=True
    )

    designation = models.CharField(
        max_length=100,
        blank=True
    )

    def __str__(self):
        return self.user.username
