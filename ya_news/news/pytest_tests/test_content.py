import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_ten_news_on_main_page(client):
    url_news_home = reverse('news:home')
    response = client.get(url_news_home)
    news_count = response.context['object_list'].count()
    assert news_count <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted_by_date(client):
    url_news_home = reverse('news:home')
    response = client.get(url_news_home)
    news = response.context['object_list']
    all_dates = [object_news.date for object_news in news]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_sorted_by_creation_date(client, news):
    url_news_detail = reverse('news:detail', args=[news.id])
    response = client.get(url_news_detail)
    assert 'news' in response.context
    news = response.context['news']
    comments = news.comment_set.all()
    comment_dates = [comment.created for comment in comments]
    sorted_dates = sorted(comment_dates)
    assert comment_dates == sorted_dates


@pytest.mark.parametrize('client_fixture, form_exists', [
    ('client', False),
    ('author_client', True),
])
def test_comment_form_visibility(client_fixture, form_exists, request, news):
    client = request.getfixturevalue(client_fixture)
    url_news_detail = reverse('news:detail', args=[news.id])
    response = client.get(url_news_detail)
    assert ('form' in response.context) == form_exists


def test_comment_form_type_for_author(author_client, news):
    url_news_detail = reverse('news:detail', args=[news.id])
    response = author_client.get(url_news_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
