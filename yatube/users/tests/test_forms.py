from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CreationForm

User = get_user_model()


class UserCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='authorized')
        cls.form = CreationForm()

    def test_create_post(self):
        """Валидная форма создает запись в User."""
        tasks_count = User.objects.count()
        form_data = {
            'password1': 'passcreate',
            'password2': 'passcreate',
            'username': 'testusername',
            'first_name': 'testfirstname',
            'email': 'email@mail.com',
            'last_name': 'testlastname',
        }
        response = UserCreateFormTests.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), tasks_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='testusername',
                first_name='testfirstname',
                email='email@mail.com',
                last_name='testlastname',
            ).exists()
        )
