from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

class DeleteAccountForm(forms.Form):
    """
    Simple confirmation form for account deletion.
    """
    confirm = forms.BooleanField(
        required=True,
        label="I understand that this action cannot be undone.",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('confirm'):
            raise forms.ValidationError("You must confirm that you want to delete your account.")
        return cleaned_data
