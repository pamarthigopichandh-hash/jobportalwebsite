from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings

from .models import Job, JobApplication, JobSeekerProfile
from .forms import EmployerUserProfileForm, RegisterForm, LoginForm, JobPostForm, JobApplicationForm
from .profileform import JobSeekerProfileForm


# ==========================================================
# HOME
# ==========================================================
@never_cache
def home(request):
    return render(request, 'jobapp/home.html')


# ==========================================================
# REGISTER
# ==========================================================
from django.contrib import messages
from django.shortcuts import render, redirect


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Account created successfully. Please login."
            )

            # ✅ go to login page
            return redirect("login")

    else:
        form = RegisterForm()

    return render(
        request,
        "jobapp/register.html",
        {"form": form}
    )
    
    
    
# ==========================================================
# LOGIN
# ==========================================================

from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.cache import never_cache


@never_cache
def login_view(request):

    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            user = form.get_user()
            selected_role = form.cleaned_data["role"]

            # ✅ ROLE VALIDATION
            if user.role != selected_role:

                form.add_error(
                    None,
                    "Selected role does not match your account."
                )

            else:
                login(request, user)

                messages.success(
                    request,
                    "Login successful"
                )

                if user.role == "jobseeker":
                    return redirect("jobs")

                elif user.role == "employer":
                    return redirect("employer_dashboard")

        else:
            messages.error(
                request,
                "Invalid username or password."
            )

    else:
        form = LoginForm()

    return render(
        request,
        "jobapp/login.html",
        {"form": form}
    )

# ==========================================================
# LOGOUT
# ==========================================================
@never_cache
@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request,"Account Logout successfully")
    return redirect('login')


# ==========================================================
# JOB SEEKER PROFILE
# ==========================================================
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import JobSeekerProfile, Experience, Education
from .forms import JobSeekerProfileForm



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages


@login_required
def jobseeker_profile(request):

    profile, _ = JobSeekerProfile.objects.get_or_create(
        user=request.user
    )

    edit_mode = request.GET.get("edit") == "1"

    # ================= SAVE =================
    if request.method == "POST":

        form = JobSeekerProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            profile_obj = form.save(commit=False)
            profile_obj.user = request.user
            profile_obj.save()

            messages.success(request, "Profile Updated ✅")

            # ✅ FORCE REFRESH OBJECT
            return redirect("jobseeker_profile")

        else:
            print(form.errors)

    else:
        form = JobSeekerProfileForm(instance=profile)

    # ✅ ALWAYS FETCH UPDATED DATA
    profile = JobSeekerProfile.objects.get(user=request.user)

    experiences = Experience.objects.filter(user=request.user)
    educations = Education.objects.filter(user=request.user)

    return render(
        request,
        "jobapp/jobseeker_profile.html",
        {
            "profile": profile,
            "form": form,
            "edit_mode": edit_mode,
            "experiences": experiences,
            "educations": educations,
        },
    )
    
    
from django.db.models import Q
# ==========================================================
# JOB LIST
# ==========================================================

from django.shortcuts import render
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Job

@login_required
@never_cache
def jobs_page(request):

    jobs = Job.objects.all().order_by("-created_at")

    # ================= SEARCH FILTER =================

    title = request.GET.get("title")
    location = request.GET.get("location")
    category = request.GET.get("category")
    job_type = request.GET.get("job_type")

    if title:
        jobs = jobs.filter(
            Q(title__icontains=title) |
            Q(company__company_name__icontains=title)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if category and category != "All":
        jobs = jobs.filter(category=category)

    if job_type and job_type != "All":
        jobs = jobs.filter(job_type=job_type)

    # ================= SIDEBAR MULTI FILTER =================

    locations = request.GET.getlist("loc")
    types = request.GET.getlist("type")

    if locations:
        jobs = jobs.filter(location__in=locations)

    if types:
        jobs = jobs.filter(job_type__in=types)

    # ================= PAGINATION =================

    paginator = Paginator(jobs, 6)
    page_number = request.GET.get("page")
    jobs = paginator.get_page(page_number)

    # ================= FILTER COUNTS =================

    location_counts = (
        Job.objects.values("location")
        .annotate(total=Count("id"))
    )

    jobtype_counts = (
        Job.objects.values("job_type")
        .annotate(total=Count("id"))
    )

    context = {
        "jobs": jobs,
        "location_counts": location_counts,
        "jobtype_counts": jobtype_counts,
    }

    return render(request, "jobapp/jobs.html", context)
    
# ==========================================================
# JOBs PAGE
# ==========================================================
from django.http import JsonResponse
from django.template.loader import render_to_string


from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Count

@never_cache
def ajax_job_filter(request):

    jobs = Job.objects.all().order_by("-created_at")

    locations = request.GET.getlist("location[]")
    job_types = request.GET.getlist("job_type[]")

    page = request.GET.get("page", 1)

    if locations:
        jobs = jobs.filter(location__in=locations)

    if job_types:
        jobs = jobs.filter(job_type__in=job_types)

    # ---------- PAGINATION ----------
    paginator = Paginator(jobs, 6)
    jobs_page = paginator.get_page(page)

    # ---------- FILTER COUNTS ----------
    location_counts = (
        Job.objects.values("location")
        .annotate(total=Count("id"))
    )

    type_counts = (
        Job.objects.values("job_type")
        .annotate(total=Count("id"))
    )

    jobs_html = render_to_string(
        "jobapp/job_cards.html",
        {"jobs": jobs_page}
    )

    filters_html = render_to_string(
        "jobapp/filter_counts.html",
        {
            "location_counts": location_counts,
            "type_counts": type_counts
        }
    )

    pagination_html = render_to_string(
        "jobapp/pagination.html",
        {"jobs": jobs_page}
    )

    return JsonResponse({
        "jobs": jobs_html,
        "filters": filters_html,
        "pagination": pagination_html
    })


# ==========================================================
# JOB DETAIL
# ==========================================================
@never_cache
@login_required
def job_detail(request, id):
    job = get_object_or_404(Job, id=id)
    already_applied = JobApplication.objects.filter(user=request.user, job=job).exists()

    return render(request, 'jobapp/job_detail.html', {
        'job': job,
        'already_applied': already_applied
    })


# ==========================================================
# APPLY JOB
# =========================================================


#from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Job, JobApplication
from .forms import JobApplicationForm
from .ats_engine import extract_resume_text, calculate_ats_score
from .models import DecisionLog  # if you added logging
@never_cache
@login_required
def apply_job(request, id):
    job = get_object_or_404(Job, id=id)

    # Prevent duplicate applications
    if JobApplication.objects.filter(user=request.user, job=job).exists():
        messages.error(request, "You already applied for this job.")
        return redirect("job_detail", id=job.id)

    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.job = job

            # ✅ Save first so resume file is written to disk
            application.save()

            # Now safely extract resume text
            resume_text = extract_resume_text(application.resume.path)
            score, matched, missing = calculate_ats_score(job.skills_required, resume_text)
            application.ats_score = score

            # Decide status immediately
            if score >= 70:
                application.status = "Accepted"
                application.is_auto_shortlisted = True

             # Generate exam link
                from django.urls import reverse
                exam_url = request.build_absolute_uri(
                reverse('start_exam', args=[application.exam_token])
                )

                subject = "Application Shortlisted - Online Examination"

                message = (
                f"Hello {application.user.username},\n\n"
                f"🎉 Congratulations!\n\n"
                f"You have been shortlisted for the position "
                f"'{job.title}' at {job.company}.\n\n"
                f"Next Step: Complete the Online Examination.\n\n"
                f"Click the link below to start your exam:\n"
                f"{exam_url}\n\n"
                f"Important:\n"
                f"- This link is unique to you.\n"
                f"- Do not share this link.\n\n"
                f"Best Regards,\n{job.company}"
                )

            elif score < 40:
                application.status = "Rejected"
                subject = "Job Application Rejected"
                message = (
                    f"Hello {application.user.username},\n\n"
                    f"Thank you for applying for '{job.title}' "
                    f"at {job.company}.\n\n"
                    f"We regret to inform you that your application was not selected "
                    f"(ATS score {score}%).\n\n"
                    f"Best Regards,\n{job.company}"
                )
            else:
                application.status = "Pending"
                subject = "Application Received"
                message = (
                    f"Hello {application.user.username},\n\n"
                    f"Your application for '{job.title}' "
                    f"has been received and is under review.\n\n"
                    f"Best Regards,\n{job.company}"
                )

            # Save updated status and ATS score
            application.save()

            # Optional: log ATS decision
            try:
                DecisionLog.objects.create(
                    application=application,
                    employer=job.employer,
                    action=application.status,
                    ats_score=score,
                )
            except:
                pass  # skip if DecisionLog not defined

            # Send mail immediately
            if application.user.email:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [application.user.email],
                    fail_silently=False,
                )

            messages.success(request, f"Job applied successfully! Status: {application.status}")
            return redirect("applied_jobs")
    else:
        form = JobApplicationForm()

    return render(request, "jobapp/apply_job.html", {"job": job, "form": form})

# ==========================================================
# DASHBOARD
# ==========================================================



from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import JobApplication

@login_required
@never_cache
def jobseeker_dashboard(request):
    qs = JobApplication.objects.filter(user=request.user)

    context = {
        "total_applied": qs.count(),
        "pending_count": qs.filter(status='Pending').count(),
        "viewed_count": qs.filter(status='Viewed').count(),
        "accepted_count": qs.filter(status='Accepted').count(),
        "rejected_count": qs.filter(status='Rejected').count(),
        "withdrawn_count": qs.filter(status='Withdrawn').count(),
        "recent_apps": qs.order_by('-applied_at')[:5],
    }
    return render(request, "jobapp/jobseeker_dashboard.html", context)


# ==========================================================
# APPLIED JOBS
# ==========================================================

@login_required
@never_cache
def applied_jobs(request):
    applications = JobApplication.objects.filter(user=request.user)

    accepted_jobs = applications.filter(status="Accepted")
    rejected_jobs = applications.filter(status="Rejected")
    viewed_jobs   = applications.filter(status="Viewed")
    withdrawn_jobs = applications.filter(status="Withdrawn")

    context = {
        "applications": applications,
        "accepted_jobs": accepted_jobs,
        "rejected_jobs": rejected_jobs,
        "viewed_jobs": viewed_jobs,
        "withdrawn_jobs": withdrawn_jobs,
        "accepted_count": accepted_jobs.count(),
        "rejected_count": rejected_jobs.count(),
        "viewed_count": viewed_jobs.count(),
        "withdrawn_count": withdrawn_jobs.count(),
    }
    return render(request, "jobapp/applied_jobs.html", context)



# ==========================================================
# EMPLOYER DASHBOARD
# ==========================================================




from django.shortcuts import render,redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Job

# ------------------employer_profile------------------------

from .models import EmployerProfile, EmployerUserProfile


@login_required
@never_cache
def employer_profile(request):

    profile, _ = EmployerProfile.objects.get_or_create(
        user=request.user
    )

    user_profile, _ = EmployerUserProfile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        "empapp/employer_profile.html",
        {
            "profile": profile,
            "user_profile": user_profile
        }
    )


# -------------employer_edit_profile---------------------------------

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import EmployerProfile
from .forms import EmployerProfileForm

from .models import EmployerUserProfile



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import EmployerProfile, EmployerUserProfile
from .forms import EmployerProfileForm, EmployerUserProfileForm


@login_required
@never_cache
def edit_employer_profile(request):

    profile = EmployerProfile.objects.get(user=request.user)
    user_profile = EmployerUserProfile.objects.get(user=request.user)

    if request.method == "POST":

        form = EmployerProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        user_form = EmployerUserProfileForm(
            request.POST,
            request.FILES,
            instance=user_profile
        )

        if form.is_valid() and user_form.is_valid():

            form.save()
            user_form.save()

            return redirect("employer_profile")

        else:
            print("Employer Errors:", form.errors)
            print("User Errors:", user_form.errors)

    else:
        form = EmployerProfileForm(instance=profile)
        user_form = EmployerUserProfileForm(instance=user_profile)

    return render(
        request,
        "empapp/edit_employer_profile.html",
        {
            "form": form,
            "user_form": user_form,
            "profile": profile,
            "user_profile": user_profile,
        }
    )

# ---------------company-------------------
from django.shortcuts import render, get_object_or_404
from .models import EmployerProfile, Job


def company_detail(request, slug):

    company = get_object_or_404(
        EmployerProfile,
        slug=slug
    )

    jobs = Job.objects.filter(
        employer=company.user
    ).order_by("-created_at")

    return render(
        request,
        "jobapp/company_detail.html",
        {
            "company": company,
            "jobs": jobs
        }
    )
    



@login_required(login_url='login')
@never_cache
def employer_dashboard(request):
    if request.user.role != 'employer':
        return redirect('login')


    jobs = (
        Job.objects.filter(employer=request.user)
        .annotate(
            total_count=Count('applications'),
            pending_count=Count('applications', filter=Q(applications__status='Pending')),
            accepted_count=Count('applications', filter=Q(applications__status='Accepted')),  
            rejected_count=Count('applications', filter=Q(applications__status='Rejected')),
            viewed_count=Count('applications', filter=Q(applications__status='Viewed')),
        )
        .order_by('-created_at')
    )

    return render(request, 'empapp/employer_dashboard.html', {'jobs': jobs})


# ==========================================================
# POST JOB
# ==========================================================
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from .forms import JobPostForm
from .models import ExamQuestion
from .exam_utils import (
    extract_questions_from_pdf,
    extract_questions_from_docx,
    auto_generate_questions
)






@login_required
@never_cache
def employer_post_job(request):

    # =============================
    # ROLE CHECK
    # =============================
    if getattr(request.user, "role", None) != "employer":
        return HttpResponseForbidden("Access Denied")

    if request.method == "POST":

        form = JobPostForm(request.POST, request.FILES)

        if form.is_valid():

            # =============================
            # SAVE JOB FIRST
            # =============================
            job = form.save(commit=False)
            if not job.work_mode:
                job.work_mode = "Onsite"
            job.employer = request.user
            job.save()

            print("✅ JOB SAVED")

            questions = []

            # =============================
            # EXAM FILE PROCESSING
            # =============================
            if job.exam_file:

                try:
                    file_path = job.exam_file.path.lower()

                    if file_path.endswith(".pdf"):
                        questions = extract_questions_from_pdf(file_path)

                    elif file_path.endswith(".docx"):
                        questions = extract_questions_from_docx(file_path)

                except Exception as e:
                    print("Exam extraction error:", e)

            # =============================
            # AUTO GENERATE IF EMPTY
            # =============================
            if not questions:
                try:
                    questions = auto_generate_questions(
                        job.title,
                        job.skills_required
                    )
                except Exception as e:
                    print("AI generation error:", e)

            # =============================
            # SAVE QUESTIONS
            # =============================
            if questions:

                from jobapp.models import ExamQuestion, ExamOption

                ExamQuestion.objects.filter(job=job).delete()

                for q in questions:

                    question_obj = ExamQuestion.objects.create(
                        job=job,
                        text=q.get("question", "")
                    )

                    correct_letter = str(
                        q.get("answer", "")
                    ).strip().upper()[:1]

                    for index, opt in enumerate(
                        q.get("options", [])
                    ):

                        option_letter = chr(65 + index)

                        ExamOption.objects.create(
                            question=question_obj,
                            text=opt.strip(),
                            is_correct=(
                                option_letter == correct_letter
                            )
                        )

            # =============================
            # SUCCESS MESSAGE
            # =============================
            messages.success(
                request,
                "Job posted successfully!"
            )

            return redirect("employer_dashboard")

        else:
            print("❌ FORM ERRORS:", form.errors)

    else:
        form = JobPostForm(
            initial={"deadline": now().date()}
        )

    return render(
        request,
        "empapp/employer_post_a_job.html",
        {
            "form": form,
            "today": now().date().isoformat(),
        },
    )
    
    
# ==========================================================
# EDIT JOB
# ==========================================================
from datetime import date

@login_required
def employer_edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user)

    if request.method == "POST":
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('employer_dashboard')
    else:
        form = JobPostForm(instance=job)

    return render(request, 'empapp/employer_post_a_job.html', {
        'form': form,
        'edit_mode': True,
        'today': date.today().isoformat()   # ✅ ADD THIS
    })



# ==========================================================
# DELETE JOB
# ==========================================================
@login_required
def employer_delete_job(request, pk):
    if request.user.role != 'employer':
        return HttpResponseForbidden("Access Denied")

    job = get_object_or_404(Job, pk=pk, employer=request.user)

    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job deleted successfully!")
        return redirect('employer_dashboard')

    return render(request, 'empapp/employer_confirm_delete.html', {'job': job})


# ==========================================================
# VIEW APPLICANTS
# ==========================================================
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Job, JobApplication, JobSeekerProfile

def normalize_skills(skills_str):
    return set(
        s.strip().lower().replace(" ", "")
        for s in (skills_str or "").split(",")
        if s.strip()
    )

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Job, JobApplication
from .ats_engine import extract_resume_text, calculate_ats_score

@login_required
@never_cache
def employer_view_applicants(request, job_id):
    if request.user.role != 'employer':
        return HttpResponseForbidden("Access Denied")

    job = get_object_or_404(Job, id=job_id, employer=request.user)
    applications = JobApplication.objects.filter(job=job).order_by('-ats_score')

    # ===== FILTER SYSTEM =====
    level = request.GET.get("level")
    if level == "top":
        applications = applications.filter(ats_score__gte=70)
    elif level == "medium":
        applications = applications.filter(ats_score__range=(40, 69))
    elif level == "low":
        applications = applications.filter(ats_score__lt=40)
    elif level == "recommended":
        applications = applications.filter(is_auto_shortlisted=True)

    # ===== ENRICH APPLICATIONS WITH ATS SCORING + EXAM INFO =====
    for app in applications:
        resume_path = app.resume.path if app.resume else None
        resume_text = extract_resume_text(resume_path) if resume_path else ""

        ats_score, matched, missing = calculate_ats_score(job.skills_required, resume_text)

        # Attach ATS info (not saved to DB, just for template)
        app.ats_score = ats_score
        app.matched_skills = ", ".join(matched) if matched else None
        app.missing_skills = ", ".join(missing) if missing else None
        app.is_auto_shortlisted = ats_score >= 70

        # ✅ Exam info (pulled from DB, always numeric)
        app.exam_score_display = app.exam_score if app.exam_score is not None else 0
        app.exam_status = app.status  # "Shortlisted", "Rejected", etc.

        # ✅ Attempt status (latest attempt if exists)
        latest_attempt = app.exam_attempts.order_by("-started_at").first()
        app.attempt_status = latest_attempt.status if latest_attempt else "Not Attempted"

    # ===== STATS =====
    total_count = job.applications.count()
    recommended_count = job.applications.filter(is_auto_shortlisted=True).count()
    top_count = job.applications.filter(ats_score__gte=70).count()

    context = {
        'job': job,
        'applications': applications,
        'total_count': total_count,
        'recommended_count': recommended_count,
        'top_count': top_count,
    }
    return render(request, 'empapp/employer_applicants.html', context)



@login_required
def recommend_application(request, application_id):
    application = get_object_or_404(
        JobApplication,
        id=application_id,
        job__employer=request.user
    )

    # Use the correct field from your model
    application.is_auto_shortlisted = True
    application.status = "viewed"   # optional: mark as viewed when recommended
    application.save()

    messages.success(request, "Applicant added to Recommended list!")
    return redirect('employer_view_applicants', job_id=application.job.id)


# ==========================================================
# UPDATE APPLICATION STATUS
# ==========================================================

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import JobApplication

@login_required
@ never_cache
def update_application_status(request, application_id, action):
    
    
    application = get_object_or_404(
        JobApplication,
        id=application_id,
        job__employer=request.user  # only employer can update
    )

    action = action.lower()

    if action == "accept":
        application.status = "Accepted"
        subject = "Job Application Accepted"
        message = (
            f"Hello {application.user.username},\n\n"
            f"Congratulations!\n\n"
            f"Your application for '{application.job.title}' "
            f"at {application.job.company} has been ACCEPTED.\n\n"
            f"Best Regards,\n{application.job.company}"
        )

    elif action == "reject":
        application.status = "Rejected"
        subject = "Job Application Rejected"
        message = (
            f"Hello {application.user.username},\n\n"
            f"Thank you for applying for '{application.job.title}' "
            f"at {application.job.company}.\n\n"
            f"We regret to inform you that your application was not selected.\n\n"
            f"Best Regards,\n{application.job.company}"
        )

    elif action == "viewed":
        application.status = "Viewed"
        subject = "Application Viewed"
        message = (
            f"Hello {application.user.username},\n\n"
            f"Your application for '{application.job.title}' has been viewed.\n\n"
            f"Best Regards,\nJob Portal Team"
        )

    else:
        messages.error(request, "Invalid action.")
        return redirect('employer_dashboard')

    # Save status immediately
    application.save()
    DecisionLog.objects.create( application=application, employer=request.user, action=application.status, ats_score=application.ats_score, )

    # Send mail immediately
    if application.user.email:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [application.user.email],
            fail_silently=False,
        )

    messages.success(request, f"Application status updated to {application.status}.")
    return redirect('employer_view_applicants', job_id=application.job.id)
@login_required
def withdraw_application(request, pk):
    # Only allow the logged-in seeker to withdraw their own application
    application = get_object_or_404(JobApplication, id=pk, user=request.user)

    if request.method == "POST":
        # Send confirmation email before deleting
        if application.user.email:
            send_mail(
                "Application Withdrawn",
                f"Hello {application.user.username},\n\n"
                f"You have successfully withdrawn your application for '{application.job.title}' "
                f"at {application.job.company}.\n\n"
                f"Best Regards,\nJob Portal Team",
                settings.DEFAULT_FROM_EMAIL,
                [application.user.email],
                fail_silently=False,
            )

        # Delete the application record
        application.delete()

        messages.success(request, "Your application has been withdrawn and deleted.")
        return redirect("applied_jobs")

    # Render confirmation page for GET requests
    return render(request, "jobapp/withdraw_confirm.html", {"application": application})

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Job, JobApplication

@login_required
def employer_accepted_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    applicants = JobApplication.objects.filter(job=job, status='Accepted')
    return render(request, 'empapp/employer_accepted_applicants.html', {
        'job': job,
        'applicants': applicants
    })

@login_required
def employer_rejected_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    applicants = JobApplication.objects.filter(job=job, status='Rejected')
    return render(request, 'empapp/employer_rejected_applicants.html', {
        'job': job,
        'applicants': applicants
    })
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import JobApplication



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import JobApplication

@login_required
def withdraw_application(request, pk):
    application = get_object_or_404(JobApplication, id=pk, user=request.user)
    application.status = "Withdrawn"  
    application.save()

    subject = "Application Withdrawn Confirmation"
    message = (
        f"Dear {request.user.username},\n\n"
        f"You have successfully withdrawn your application for the job: "
        f"{application.job.title} at {application.job.company}.\n\n"
        "Thank you for using our portal."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])

    messages.success(request, "Application withdrawn successfully. A confirmation email has been sent.")
    return redirect('applied_jobs')




@login_required
def pending_jobs(request):
    user = request.user
    applications = JobApplication.objects.filter(user=user, status='Pending').select_related('job')
    return render(request, 'jobapp/pending_jobs.html', {
        'applications': applications
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import JobApplication

@login_required
def view_application(request, application_id):
    # Only allow the logged-in seeker to view their own application
    application = get_object_or_404(JobApplication, id=application_id, user=request.user)

    context = {
        "application": application,
        "ats_score": application.ats_score,  # ✅ pass ATS score to template
    }
    return render(request, "jobapp/view_application.html", context)

#examination link 
# ======================================
# TAKE & SUBMIT EXAM - Full Exam-safe Version
# ======================================

import math
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from .models import (
    JobApplication,
    ExamQuestion,
    ExamOption,
    ExamAttempt,
    ExamAnswer,
    ExamResult
)
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from jobapp.models import JobApplication

@login_required
def start_exam(request, token):
    """
    Simple landing page before the exam.
    Fetches the job application using the unique exam token.
    """
    application = get_object_or_404(
        JobApplication,
        exam_token=token,
        user=request.user
    )

    return render(request, "exam/start_exam.html", {
        "application": application
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
import math

from .models import JobApplication, ExamQuestion, ExamOption, ExamAnswer, ExamAttempt, ExamResult
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from jobapp.models import JobApplication, ExamQuestion, ExamOption, ExamAnswer, ExamAttempt, ExamResult
import math

@login_required
def take_exam(request, exam_token):
    application = get_object_or_404(JobApplication, exam_token=exam_token, user=request.user)

    if application.exam_completed:
        messages.warning(request, "You have already completed this exam.")
        return redirect("applied_jobs")

    questions = ExamQuestion.objects.filter(job=application.job).prefetch_related("options")
    if not questions.exists():
        messages.error(request, "No exam questions available for this job.")
        return redirect("applied_jobs")

    if request.method == "POST":
        total_questions = questions.count()
        passing_marks = math.ceil(total_questions / 2)
        score = 0

        # Create attempt
        attempt = ExamAttempt.objects.create(application=application)

        for q in questions:
            option_id = request.POST.get(f"q{q.id}")
            if option_id:
                option = ExamOption.objects.filter(id=option_id, question=q).first()
                if option and option.is_correct:
                    score += 1

                ExamAnswer.objects.create(
                    attempt=attempt,
                    question=q,
                    answer_text=option.text if option else "",
                    is_correct=option.is_correct if option else False
                )

        # Update attempt
        attempt.score = score
        attempt.completed_at = now()
        attempt.status = "Passed" if score >= passing_marks else "Failed"
        attempt.save()

        # Update application
        application.exam_score = score
        application.final_score = score
        application.exam_completed = True
        application.status = "Accepted" if score >= passing_marks else "Rejected"
        application.save()

        # Save exam result
        result, _ = ExamResult.objects.update_or_create(
            application=application,
            defaults={
                "exam": application.job,
                "score": score,
                "status": "Shortlisted" if score >= passing_marks else "Rejected"
            }
        )

        # Send email
        if application.user.email:
            result_status = "Passed" if score >= passing_marks else "Failed"
            subject = f"Exam Result - {application.job.title}"
            message = f"""
Dear {application.user.username},

Your exam for "{application.job.title}" has been completed.

Score: {score} / {total_questions}
Result: {result_status}

Thank you for participating.

Best Regards,
Recruitment Team
"""
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [application.user.email], fail_silently=False)

        # In render context after POST
        return render(request, "exam/exam_submitted.html", {
    "application": application,
    "score": score,
    "total": total_questions,
    "status": attempt.status,
    "passing_marks": passing_marks,   # add this
    "exam_result": result
})

    return render(request, "exam/take_exam.html", {
        "application": application,
        "questions": questions
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import EmployerProfile
from .forms import EmployerProfileForm


# ------------------company_detail----------------
from django.shortcuts import render, get_object_or_404
from .models import EmployerProfile, Job


def company_detail(request, slug):

    company = get_object_or_404(
        EmployerProfile,
        slug=slug
    )

    jobs = Job.objects.filter(
        company=company
    ).order_by("-created_at")

    context = {
        "company": company,
        "jobs": jobs
    }

    return render(
        request,
        "jobapp/company_detail.html",
        context
    )