from http import HTTPStatus

from django.test import Client, TestCase


class ViewTestClass(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_error_page(self):
        """Проеверяет шаблон и статус ответа
        сервера для несуществующих страниц"""
        response = ViewTestClass.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
