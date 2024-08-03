from http import HTTPStatus

from django.urls import reverse

from notes.tests.conftest import TestNote


class TestRoutes(TestNote):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.public_urls = [
            cls.LOGIN_URL,
            reverse('notes:home'),
            reverse('users:logout'),
            reverse('users:signup'),
        ]
        cls.authenticated_urls = [
            cls.ADD_URL,
            cls.LIST_URL,
            cls.SUCCESS_URL,
        ]
        cls.note_specific_urls = [
            cls.EDIT_URL,
            cls.DELETE_URL,
            reverse('notes:detail', args=(cls.note.slug,)),
        ]

    def test_public_pages_are_accessible(self):
        self.verify_url_status(self.public_urls, HTTPStatus.OK)

    def test_authenticated_pages_are_accessible(self):
        self.verify_url_status(self.authenticated_urls, HTTPStatus.OK,
                               client=self.author_client)

    def test_redirects_for_anonymous_users(self):
        for url in self.authenticated_urls + self.note_specific_urls:
            with self.subTest(url=url):
                expected_redirect_url = f'{self.LOGIN_URL}?next={url}'
                self.assertRedirects(self.client.get(url),
                                     expected_redirect_url)

    def test_note_edit_and_delete_accessibility(self):
        user_accessibility = [
            (self.author_client, HTTPStatus.OK),
            (self.non_author_client, HTTPStatus.NOT_FOUND),
        ]

        for user, status in user_accessibility:
            self.verify_url_status(self.note_specific_urls, status,
                                   client=user)

    def verify_url_status(self, urls, expected_status, client=None):
        client = client or self.client
        for url in urls:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)
