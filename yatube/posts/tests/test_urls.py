from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='authorized')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self):
        cache.clear()

    def test_urls_exists_at_desired_location(self):
        """URL-адреса доступны любому пользователю."""
        response_url_names = {
            '/': HTTPStatus.OK,
            f'/profile/{PostURLTests.user.username}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            f'/profile/{PostURLTests.author.username}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
        }
        for url, expected_response in response_url_names.items():
            with self.subTest(url=url):
                response = PostURLTests.guest_client.get(url, follow=False)
                self.assertEqual(response.status_code, expected_response)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = PostURLTests.authorized_user.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_at_desired_location_author(self):
        """Страница /posts/<post_id>/edit/ доступна авторизованному автору."""
        response = PostURLTests.authorized_author.get(f'/posts/'
                                                      f'{PostURLTests.post.id}'
                                                      f'/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_task_list_url_redirect_anonymous_on_auth_login(self):
        """Страницы /create/, /posts/<post_id>/edit/ и
        /posts/<post_id>/comment/ перенаправит
        анонимного пользователя на страницу логина."""
        url_list = [
            '/create/',
            f'/posts/{PostURLTests.post.id}/edit/',
            f'/posts/{PostURLTests.post.id}/comment/',
        ]
        for url in url_list:
            with self.subTest(url=url):
                response = PostURLTests.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, f'/auth/login/?next={url}')

    def test_task_list_url_redirect_authorized_on_post_detail(self):
        """Страница /posts/<post_id>/edit/
        перенаправит авторизованного не автора на страницу поста.
        """
        url_list = [
            f'/posts/{PostURLTests.post.id}/edit/',
        ]
        for url in url_list:
            with self.subTest(url=url):
                response = PostURLTests.authorized_user.get(url, follow=True)
                self.assertRedirects(
                    response, f'/posts/{PostURLTests.post.id}/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/profile/{PostURLTests.user.username}/': 'posts/profile.html',
            f'/profile/{PostURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/posts/{PostURLTests.post.id}/edit/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = PostURLTests.authorized_author.get(url)
                self.assertTemplateUsed(response, template)
