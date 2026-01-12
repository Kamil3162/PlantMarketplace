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
        print("invoke metrhod clean_passwordsa")
        password = self.cleaned_data.get('password')
        if password and len(password) < 8:
            raise forms.ValidationError("Hasło musi mieć co najmniej 8 znaków")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        user.set_password(password)

        if commit:
            user.save()
        return user


class UserResetPassword(forms.ModelForm):
    # Opcjonalne pole hasła - jeśli puste, hasło nie będzie zmieniane
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Zostaw puste, jeśli nie chcesz zmieniać hasła"
    )

    class Meta:
        model = User
        fields = ('password', )

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


class CustomUserForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    twoj_stary = forms.CharField(max_length=10, required=False)

    def inform(self, commit=True):
        print(self.fields)
        print(self.declared_fields)

    def is_valid(self):
        build_data = super().is_valid()
        print(build_data)
        return build_data

    def clean_twoj_stary(self):
        print("clean essasito")
        print(f"Wartość: {self.cleaned_data.get('twoj_stary')}")
        return self.cleaned_data.get('twoj_stary')

    def get_context(self):
        context = super().get_context()
        print(context)
        return context

    def save(self):
        data = self.cleaned_data
        user = CustomUser.objects.create_user(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
        )
        return user