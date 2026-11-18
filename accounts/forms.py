from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import CustomUser


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a secure password (min. 8 characters)',
            'autocomplete': 'new-password'
        }),
        min_length=8,
        help_text="Password must contain at least 8 characters."
    )
    password_confirm = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter your password',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'employee_id',
            'department',
            'contact_number',
            'profile_photo',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. jdelacruz'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. juan@school.edu'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Juan'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dela Cruz'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. EMP-2026-001'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. High School Faculty / HR'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +63 912 345 6789'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Required fields validation
        self.fields['username'].required = True
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['role'].required = True

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError("A user with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address is already registered.")
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id:
            if CustomUser.objects.filter(employee_id__iexact=employee_id).exists():
                raise ValidationError("This Employee ID is already registered to another user.")
        return employee_id

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', "Passwords do not match. Please re-enter.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Hash the password properly using Django authentication
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username or email',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        login_input = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if login_input and password:
            # Check if input is email or username
            user_obj = None
            if '@' in login_input:
                try:
                    user_match = CustomUser.objects.get(email__iexact=login_input)
                    user_obj = authenticate(username=user_match.username, password=password)
                except CustomUser.DoesNotExist:
                    user_obj = None
            else:
                user_obj = authenticate(username=login_input, password=password)

            if user_obj is None:
                raise ValidationError("Invalid username/email or password. Please verify your credentials and try again.")
            if not user_obj.is_active:
                raise ValidationError("This account is currently disabled. Please contact your administrator.")

            self.user = user_obj
        return cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'contact_number',
            'department',
            'employee_id',
            'profile_photo',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_user = self.instance
        if CustomUser.objects.filter(email__iexact=email).exclude(pk=current_user.pk).exists():
            raise ValidationError("This email is already taken by another account.")
        return email
