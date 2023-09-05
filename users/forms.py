from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm as DjangoAuthenticationForm
from django.core.exceptions import ValidationError
from users.utils import send_email
from users.models import User


class AuthenticationForm(DjangoAuthenticationForm):

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(
                self.request,
                email=email,
                password=password,
            )
            if not self.user_cache.email_verify:
                send_email(self.request, self.user_cache)
                raise ValidationError(
                    'Почта не подтверждена, пожалуйста, проверьте почтовый ящик',
                    code='invalid_login',
                )

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']
