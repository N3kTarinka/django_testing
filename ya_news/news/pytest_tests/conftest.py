import pytest

from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(username='Гость')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def user_client(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news, author=author, text='Текст комментария'
    )
    return comment


@pytest.fixture
def news_for_main_page():
    today = timezone.now()

    News.objects.bulk_create(
        News(
            title=f'Заголовок {index + 1}',
            text=f'Текст {index + 1}',
            date=today - timezone.timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments_for_same_news(author, news):
    for index in range(10):
        Comment.objects.create(
            news=news, author=author, text=f'Текст {index + 1}'
        )
