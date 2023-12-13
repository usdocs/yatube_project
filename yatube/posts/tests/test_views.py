import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        articles = []
        for i in range(15):
            articles.append(
                Post(author=cls.author,
                     text=f'Текст №{i}',
                     group=cls.group,
                     )
            )
        Post.objects.bulk_create(articles)

    def setUp(self):
        cache.clear()

    def test_pages_contains_expected_records(self):
        """Страницы содержат нужное кол-во постов"""
        templates_page = {
            reverse('posts:index'): 10,
            reverse('posts:index') + '?page=2': 5,
            reverse('posts:group_list',
                    kwargs={'slug': PaginatorViewsTest.group.slug}): 10,
            reverse('posts:group_list',
                    kwargs={'slug': PaginatorViewsTest.group.slug})
            + '?page=2': 5,
            reverse('posts:profile',
                    kwargs={'username': PaginatorViewsTest.author}): 10,
            reverse('posts:profile',
                    kwargs={'username': PaginatorViewsTest.author})
            + '?page=2': 5,
        }
        for reverse_name, count in templates_page.items():
            with self.subTest(reverse_name=reverse_name):
                response = PaginatorViewsTest.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), count)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
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
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            author=cls.author,
            text='Текст №1',
            group=cls.group,
            image=cls.uploaded,
        )

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': PostViewsTest.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': PostViewsTest.author}):
            'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': 1}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': 1}):
            'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = PostViewsTest.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """Шаблоны index, group_list и profile
        сформированы с правильным контекстом."""
        reverse_names = [
            reverse('posts:index'),
            reverse('posts:profile',
                    kwargs={'username': PostViewsTest.author}),
            reverse('posts:group_list',
                    kwargs={'slug': PostViewsTest.group.slug}),
        ]
        for reverse_name in reverse_names:
            response = PostViewsTest.client.get(reverse_name)
            object_list = response.context['page_obj']
            templates_object_context = {
                object_list[0].author: PostViewsTest.author,
                object_list[0].text: 'Текст №1',
                object_list[0].group: PostViewsTest.group,
                object_list[0].image: 'posts/small.gif',
            }
            for object, expected in templates_object_context.items():
                with self.subTest(object=object):
                    self.assertEqual(object, expected)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (PostViewsTest.client.get(reverse
                    ('posts:post_detail', kwargs={'post_id': 1})))
        object = response.context['post']
        templates_object_context = {
            object.author.username: 'author',
            object.text: 'Текст №1',
            object.group.title: 'Тестовая группа',
            object.image: 'posts/small.gif',
        }
        for object, expected in templates_object_context.items():
            with self.subTest(object=object):
                self.assertEqual(object, expected)

    def test_forms_pages_show_correct_context(self):
        """Шаблон post_create и post_edit
        сформирован с правильным контекстом."""
        response_names = [
            PostViewsTest.authorized_user.get(reverse('posts:post_create')),
            PostViewsTest.authorized_author.
            get(reverse('posts:post_edit', kwargs={'post_id': 1})),
        ]
        for response in response_names:
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
                'image': forms.fields.ImageField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_post_with_group_correct_context(self):
        """Пост указанной группой, отображается на страницах index,
        group_list и profile и не отображается на странице
        group_list другой группы"""
        self.group = Group.objects.create(
            title='Тестовая группа2',
            slug='Тестовый слаг2',
            description='Тестовое описание2',
        )
        self.post = Post.objects.create(
            author=PostViewsTest.author,
            text='Текст №тест',
            group=self.group,
        )
        reverse_names = {
            reverse('posts:index'): True,
            reverse('posts:group_list',
                    kwargs={'slug': PostViewsTest.group.slug}): False,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): True,
            reverse('posts:profile',
                    kwargs={'username': PostViewsTest.author}): True
        }
        for reverse_name, bool in reverse_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = PostViewsTest.client.get(reverse_name)
                object_list = response.context['page_obj']
                expected = self.post in object_list
                self.assertEqual(bool, expected)


class CacheViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.client = Client()
        Post.objects.create(
            author=cls.author,
            text='Текст №1',
        )

    def test_index_cached_page_contains_expected_records(self):
        """Страница index кешируется так как надо"""
        cache.clear()
        old_response = CacheViewsTest.client.get(reverse('posts:index'))
        Post.objects.all().delete()
        cached_response = CacheViewsTest.client.get(reverse('posts:index'))
        self.assertEqual(old_response.content, cached_response.content)
        cache.clear()
        new_response = CacheViewsTest.client.get(reverse('posts:index'))
        self.assertNotEqual(old_response.content, new_response.content)


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.second_author = User.objects.create_user(username='second_author')
        cls.user = User.objects.create_user(username='user')
        cls.second_user = User.objects.create_user(username='second_user')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        Follow.objects.create(
            author=cls.author,
            user=cls.user,
        )
        Post.objects.create(
            author=cls.author,
            text='Текст №1',
        )

    def test_create_follow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок"""
        first_follow_count = Follow.objects.count()
        (FollowViewTest.authorized_user.
         get(reverse('posts:profile_follow',
                     kwargs={'username': FollowViewTest.second_author})))
        second_follow_count = Follow.objects.count()
        self.assertEqual(first_follow_count + 1, second_follow_count)
        (FollowViewTest.authorized_user.
         get(reverse('posts:profile_unfollow',
                     kwargs={'username': FollowViewTest.second_author})))
        third_follow_count = Follow.objects.count()
        self.assertEqual(third_follow_count + 1, second_follow_count)

    def test_(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан."""
        old_posts_count_user = (Post.objects.
                                filter(author__following__user=FollowViewTest.
                                       user).count())
        old_posts_count_second_user = (Post.objects.filter
                                       (author__following__user=FollowViewTest.
                                        second_user).count())
        Post.objects.create(
            author=FollowViewTest.author,
            text='Текст №2',
        )
        new_posts_count_user = (Post.objects.
                                filter(author__following__user=FollowViewTest.
                                       user).count())
        new_posts_count_second_user = (Post.objects.filter
                                       (author__following__user=FollowViewTest.
                                        second_user).count())
        self.assertEqual(old_posts_count_user + 1, new_posts_count_user)
        self.assertEqual(old_posts_count_second_user,
                         new_posts_count_second_user)
