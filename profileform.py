from django import forms
from .models import JobSeekerProfile


class JobSeekerProfileForm(forms.ModelForm):

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.RadioSelect
    )

    class Meta:
        model = JobSeekerProfile

        
        exclude = ['user', 'is_locked', 'created_at']

        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Python, Django, HTML'
            }),
            'qualification': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'experience': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'profile_photo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
