from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class UserViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create_user(username='authorized')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.uidb64 = urlsafe_base64_encode(force_bytes(cls.user))
        cls.token = default_token_generator.make_token(cls.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_change_done'):
            'users/password_change_done.html',
            reverse('users:password_change_form'):
            'users/password_change_form.html',
            reverse('users:password_reset_compete'):
            'users/password_reset_complete.html',
            reverse('users:password_reset_confirm',
                    kwargs={'uidb64': UserViewsTest.uidb64,
                            'token': UserViewsTest.token
                            }
                    ): 'users/password_reset_confirm.html',
            reverse('users:password_reset_done'):
            'users/password_reset_done.html',
            reverse('users:password_reset_form'):
            'users/password_reset_form.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = UserViewsTest.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_page_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        response = UserViewsTest.authorized_user.get(reverse('users:signup'))
        form_fields = {
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
            'username': auth_forms.UsernameField,
            'first_name': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'last_name': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
