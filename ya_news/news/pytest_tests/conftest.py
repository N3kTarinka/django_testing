from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse

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
    today = datetime.today()

    News.objects.bulk_create(
        News(
            title=f'Заголовок {index + 1}',
            text=f'Текст {index + 1}',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments_for_same_news(author, news):
    for index in range(10):
        Comment.objects.create(
            news=news, author=author, text=f'Текст {index + 1}'
        )


@pytest.fixture
def url_users_signup():
    return reverse('users:signup')


@pytest.fixture
def url_users_login():
    return reverse('users:login')


@pytest.fixture
def url_users_logout():
    return reverse('users:logout')


@pytest.fixture
def url_news_home():
    return reverse('news:home')


@pytest.fixture
def url_news_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_comment_delete(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_comment_edit(comment):
    return reverse('news:edit', args=(comment.id,))
