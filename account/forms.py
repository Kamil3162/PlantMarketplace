from django import forms

from django.forms.models import model_to_dict
from .models import CustomUser

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
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password')

    def clean(self):
        print(self.data)
        print(self.fields)
        print(self.get_context())
        return self.cleaned_data

    def clean_data(self):
        print('clean')

    def save(self, commit=True):
        print('save')
        # user = super().save(commit=False)
        # user.set_password(self.cleaned_data['password'])
        # if commit:
        #     user.save()
        # return user