import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.author,
            post=cls.post,
            text='Тестовый коммент',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        tasks_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.id,
            'image': uploaded,
        }
        response = PostCreateFormTests.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username':
                                             PostCreateFormTests.author}))
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=PostCreateFormTests.author,
                text='Тестовый текст',
                group=PostCreateFormTests.group,
                image='posts/small.gif',
            ).exists()
        )
        new_post = Post.objects.first()
        self.assertEqual(new_post.author, PostCreateFormTests.author)
        self.assertEqual(new_post.group, PostCreateFormTests.group)

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'group': '',
        }
        response = PostCreateFormTests.authorized_author.post(
            reverse('posts:post_edit', args={self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     args={PostCreateFormTests.post.id}))
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertTrue(
            Post.objects.filter(
                author=PostCreateFormTests.author,
                text='Измененный текст',
            ).exists()
        )
        old_group_response = PostCreateFormTests.authorized_author.get(
            reverse('posts:group_list', args=(PostCreateFormTests.group.slug,))
        )
        self.assertEqual((old_group_response.context['page_obj'].
                          paginator.count), 0)


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )
        cls.post2 = Post.objects.create(
            author=cls.author,
            text='Тестовый пост2',
        )
        Comment.objects.create(
            author=cls.author,
            post=cls.post,
            text='Тестовый коммент',
        )

    def test_create_comment(self):
        """Валидная форма создает комментарий в Post."""
        comments_count = (CommentCreateFormTests.post.comments.count())
        comments_count2 = (self.post2.comments.count())
        form_data = {
            'text': 'Новый коммент',
        }
        response = CommentCreateFormTests.authorized_author.post(
            reverse('posts:add_comment', args={self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                                               args={self.post.id}))
        self.assertEqual(CommentCreateFormTests.post.comments.count(),
                         comments_count + 1)
        self.assertEqual(self.post2.comments.count(),
                         comments_count2)
        self.assertTrue(
            Comment.objects.filter(
                author=CommentCreateFormTests.author,
                text='Новый коммент',
                post=CommentCreateFormTests.post,
            ).exists()
        )
