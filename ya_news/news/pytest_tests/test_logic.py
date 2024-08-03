import random
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

COMMENT_DATA = {'text': 'Обновленный текст комментария'}
BAD_WORD = random.choice(BAD_WORDS)


def test_anonymous_user_redirect_to_login_when_posting_comment(
        client, url_news_detail, url_users_login):
    initial_count = Comment.objects.count()
    response = client.post(url_news_detail, data=COMMENT_DATA)

    assertRedirects(response, f'{url_users_login}?next={url_news_detail}')
    assert Comment.objects.count() == initial_count


def test_authenticated_user_can_add_comment(user_client, news,
                                            url_news_detail, user):
    initial_count = Comment.objects.count()
    response = user_client.post(url_news_detail, data=COMMENT_DATA)

    assertRedirects(response, f'{url_news_detail}#comments')
    assert Comment.objects.count() == initial_count + 1
    new_comment = Comment.objects.get(text=COMMENT_DATA['text'],
                                      author=user, news=news)

    assert new_comment.text == COMMENT_DATA['text']
    assert new_comment.author == user
    assert new_comment.news == news


def test_comment_with_profanity_is_rejected(user_client, url_news_detail):
    initial_count = Comment.objects.count()
    bad_word_comment = {'text': f'{BAD_WORD}...'}
    response = user_client.post(url_news_detail, data=bad_word_comment)

    assert Comment.objects.count() == initial_count
    assertFormError(response, form='form', field='text', errors=WARNING)


def test_author_can_delete_own_comment(author_client,
                                       url_comment_delete, url_news_detail):
    initial_count = Comment.objects.count()
    response = author_client.post(url_comment_delete)

    assertRedirects(response, f'{url_news_detail}#comments')
    assert Comment.objects.count() == initial_count - 1


def test_non_author_cannot_delete_comment(user_client, url_comment_delete):
    initial_count = Comment.objects.count()
    response = user_client.post(url_comment_delete)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count


def test_author_can_edit_own_comment(author_client, comment,
                                     url_comment_edit, url_news_detail):
    initial_count = Comment.objects.count()
    response = author_client.post(url_comment_edit, COMMENT_DATA)

    assertRedirects(response, f'{url_news_detail}#comments')
    assert Comment.objects.count() == initial_count
    updated_comment = Comment.objects.get(id=comment.id)

    assert updated_comment.text == COMMENT_DATA['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_non_author_cannot_edit_comment(user_client,
                                        comment, url_comment_edit):
    initial_count = Comment.objects.count()
    response = user_client.post(url_comment_edit, COMMENT_DATA)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count
    unchanged_comment = Comment.objects.get(id=comment.id)

    assert unchanged_comment.text == comment.text
    assert unchanged_comment.author == comment.author
    assert unchanged_comment.news == comment.news
