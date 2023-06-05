from django import forms
from django.core.exceptions import ValidationError


class ProfileForm(forms.Form):

    avatar = forms.ImageField(required=False)
    full_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=17, min_length=17, required=False)
    new_password1 = forms.CharField(min_length=8, widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(min_length=8, widget=forms.PasswordInput, required=False)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 != new_password2:
            raise ValidationError(message="Пароли не повторяются")
