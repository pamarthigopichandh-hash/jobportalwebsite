from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.timezone import now
from jobapp.models import User, Job, JobApplication,EmployerProfile
from django.conf import settings

from django.contrib.auth import get_user_model

# ==========================================================
# USER REGISTRATION FORM
# =========================================================


from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(UserCreationForm):

    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "role",
            "password1",
            "password2"
        ]

    # ✅ SAVE ROLE PROPERLY
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]

        if commit:
            user.save()

        return user


# ==========================================================
# LOGIN FORM
# ==========================================================
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):

    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )

from django import forms
from .models import JobSeekerProfile

# --------------------JobSeekerProfileForm
from django import forms
from .models import JobSeekerProfile


class JobSeekerProfileForm(forms.ModelForm):

    class Meta:
        model = JobSeekerProfile
        exclude = ["user"]

        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "headline": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "about": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "skills": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "qualification": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "gender": forms.Select(
                attrs={"class": "form-control"}
            ),
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }

# ==========================================================
# JOB APPLICATION FORM
# ==========================================================
class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            "full_name",
            "email",
            "phone",
            "resume",
            "cover_letter",
        ]


# ==========================================================
# JOB POST FORM (EMPLOYER)
# ==========================================================
class JobPostForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ['employer', 'created_at']
        widgets = {

            "company": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Company Name"
            }),

            "deadline": forms.DateInput(
                attrs={"type": "date"}
            ),

            "skills_required": forms.Textarea(
                attrs={
                    "placeholder":
                    "python, django, sql",
                    "rows": 3
                }
            ),

            "exam_file": forms.FileInput(
                attrs={"accept": ".pdf,.docx"}
            ),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < now().date():
            raise forms.ValidationError("Deadline cannot be in the past.")
        return deadline
    
    
    
    
    
    
    
# jobapp/forms.py
from django import forms

class ExamAnswerForm(forms.Form):
    """
    This form is intentionally left empty.
    Fields will be added dynamically in the view (take_exam).
    """
    pass



# ----------------employer-profile--------------
from django import forms
from .models import EmployerProfile, EmployerUserProfile




class EmployerProfileForm(forms.ModelForm):

    class Meta:
        model = EmployerProfile

        # ✅ ONLY editable fields
        fields = [
            "company_name",
            "logo",
            "cover_image",
            "tagline",
            "description",
            "industry",
            "company_size",
            "founded_year",
            "website",
            "location",
            "contact_email",
            "linkedin",
            "twitter",
            "facebook",
        ]

        widgets = {

            "company_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Company name"
            }),

            "tagline": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),

            "industry": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "company_size": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "founded_year": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "website": forms.URLInput(attrs={
                "class": "form-control"
            }),

            "location": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "contact_email": forms.EmailInput(attrs={
                "class": "form-control"
            }),

            "linkedin": forms.URLInput(attrs={
                "class": "form-control"
            }),

            "twitter": forms.URLInput(attrs={
                "class": "form-control"
            }),

            "facebook": forms.URLInput(attrs={
                "class": "form-control"
            }),

            "logo": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),

            "cover_image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }
# --------------------------EmployerUserProfile------------------------------

class EmployerUserProfileForm(forms.ModelForm):

    designation = forms.CharField(required=False)

    class Meta:
        model = EmployerUserProfile
        fields = ["profile_pic", "designation"]

        widgets = {
            "designation": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "HR Manager / Recruiter"
                }
            ),

            "profile_pic": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
        }