from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import Client, TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='authorized')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.uidb64 = urlsafe_base64_encode(force_bytes(cls.user))
        cls.token = default_token_generator.make_token(cls.user)

    def test_urls_exists_at_desired_location(self):
        """URL-адреса доступны любому пользователю."""
        response_url_names = {
            '/auth/login/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
            '/auth/signup/': HTTPStatus.OK,
            '/auth/reset/done/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
            '/auth/password_reset/done/': HTTPStatus.OK,
            (f'/auth/reset/{UserURLTests.uidb64}/'
             f'{UserURLTests.token}/'): HTTPStatus.OK,
        }
        for url, expected_response in response_url_names.items():
            with self.subTest(url=url):
                response = UserURLTests.guest_client.get(url)
                self.assertEqual(response.status_code, expected_response)

    def test_urls_exists_at_desired_location_authorized(self):
        """URL-адреса доступны авторизованному пользователю."""
        response_url_names = {
            '/auth/password_change/': HTTPStatus.OK,
            '/auth/password_change/done/': HTTPStatus.OK,
        }
        for url, expected_response in response_url_names.items():
            with self.subTest(url=url):
                response = UserURLTests.authorized_user.get(url)
                self.assertEqual(response.status_code, expected_response)

    def test_task_list_url_redirect_anonymous_on_admin_login(self):
        """URL-адреса перенаправят анонимного пользователя
        на страницу логина.
        """
        response_url_names = {
            '/auth/password_change/': '/auth/login/?next='
                                      '/auth/password_change/',
            '/auth/password_change/done/': '/auth/login/?next='
                                           '/auth/password_change/done/',
        }
        for url, expected_redirect in response_url_names.items():
            with self.subTest(url=url):
                response = UserURLTests.guest_client.get(url, follow=True)
                self.assertRedirects(response, expected_redirect)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/logout/': 'users/logged_out.html',
            (f'/auth/reset/{UserURLTests.uidb64}/'
             f'{UserURLTests.token}/'): 'users/password_reset_confirm.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = UserURLTests.authorized_user.get(url)
                self.assertTemplateUsed(response, template)
