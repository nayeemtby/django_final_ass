from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, ValidationError
from django.contrib.auth.models import User

from users.models import Profile


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',
                  'username', 'password1', 'password2']

    def save(self, commit: bool = True):
        if commit:
            user = super().save(commit=True)
            Profile.objects.create(user=user)
            user.is_active = False
            user.save()
            return user
        return super().save(commit)


class ProfileUpdateForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', 'lastDonationDate']

    def clean(self) -> dict[str, Any]:
        data = super().clean()
        if data['available'] == True:
            msg = []
            bg = data['bloodGroup']
            age = data['age']
            if age < 13:
                msg.append('be 13 or older')
            if bg == None or len(bg) == 0:
                msg.append('fill in your blood group')
            if len(msg) > 0:
                raise ValidationError(
                    'You must '+' and '.join(msg)+' to be available')
        return data
