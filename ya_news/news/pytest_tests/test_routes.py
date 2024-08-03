import pytest
from http import HTTPStatus
from django.urls import reverse


@pytest.mark.parametrize('url_name', [
    'news:home',
    'news:detail',
])
def test_access_for_anonymous_user(client, url_name, news):
    if url_name == 'news:detail':
        url = reverse(url_name, args=[news.id])
    else:
        url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_comment_edit_delete_access_for_author(author_client,
                                               url_comment_edit,
                                               url_comment_delete):
    edit_response = author_client.get(url_comment_edit)
    delete_response = author_client.get(url_comment_delete)
    assert edit_response.status_code == HTTPStatus.OK
    assert delete_response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('client_fixture, redirect_url', [
    ('client', reverse('users:login')),
    ('user_client', HTTPStatus.NOT_FOUND),
])
def test_comment_edit_delete_restrictions_for_anonymous_and_other_users(
        request, client_fixture, url_comment_edit,
        url_comment_delete, redirect_url):
    client = request.getfixturevalue(client_fixture)
    edit_response = client.get(url_comment_edit)
    delete_response = client.get(url_comment_delete)
    if redirect_url == HTTPStatus.NOT_FOUND:
        assert edit_response.status_code == HTTPStatus.NOT_FOUND
        assert delete_response.status_code == HTTPStatus.NOT_FOUND
    else:
        assert edit_response.status_code == HTTPStatus.FOUND
        assert delete_response.status_code == HTTPStatus.FOUND
        assert edit_response.url.startswith(redirect_url)
        assert delete_response.url.startswith(redirect_url)


@pytest.mark.parametrize('url_name', [
    'users:signup',
    'users:login',
    'users:logout',
])
def test_accessible_pages_for_anonymous_user(client, url_name):
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
