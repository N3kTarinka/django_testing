from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNote(TestCase):
    TEST_TITLE = 'Тестовый заголовок'
    TEST_TEXT = 'Тестовый текст'
    TEST_SLUG = 'note_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='автор')
        cls.non_author = User.objects.create(username='не_автор')

        cls.author_client = Client()
        cls.non_author_client = Client()

        cls.author_client.force_login(cls.author)
        cls.non_author_client.force_login(cls.non_author)

        cls.note = Note.objects.create(
            title=cls.TEST_TITLE,
            text=cls.TEST_TEXT,
            slug=cls.TEST_SLUG,
            author=cls.author
        )

        cls.LIST_URL = reverse('notes:list')
        cls.ADD_URL = reverse('notes:add')
        cls.SUCCESS_URL = reverse('notes:success')
        cls.EDIT_URL = reverse('notes:edit', args=[cls.note.slug])
        cls.DELETE_URL = reverse('notes:delete', args=[cls.note.slug])
        cls.LOGIN_URL = reverse('users:login')
