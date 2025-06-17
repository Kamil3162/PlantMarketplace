from django import forms

from django.forms.models import model_to_dict
from data.models import CustomUser

User = CustomUser
class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'password')


class UserModify(forms.ModelForm):
    # Opcjonalne pole hasła - jeśli puste, hasło nie będzie zmieniane
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Zostaw puste, jeśli nie chcesz zmieniać hasła"
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 8:
            raise forms.ValidationError("Hasło musi mieć co najmniej 8 znaków")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)

        # Zmień hasło tylko jeśli zostało podane
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user