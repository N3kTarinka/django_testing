from http import HTTPStatus

from django.template.defaultfilters import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.conftest import TestNote


class TestNoteCreation(TestNote):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'New Test Note',
            'text': 'This is a new test note',
            'slug': 'new-test-note'
        }

    def test_authenticated_user_can_create_note(self):
        self._attempt_note_creation(self.form_data)

    def test_anonymous_user_cannot_create_note(self):
        initial_notes_count = Note.objects.count()
        response = self.client.post(self.ADD_URL, data=self.form_data)
        expected_redirect_url = f'{self.LOGIN_URL}?next={self.ADD_URL}'
        self.assertRedirects(response, expected_redirect_url)
        self.assertEqual(Note.objects.count(), initial_notes_count)

    def test_creation_with_non_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        self._attempt_note_creation(self.form_data, should_fail=True)

    def test_creation_with_empty_slug(self):
        Note.objects.all().delete()
        form_data = self.form_data.copy()
        form_data.pop('slug')
        response = self.author_client.post(self.ADD_URL, data=form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.get().slug, slugify(form_data['title']))

    def test_author_can_edit_own_note(self):
        edit_data = {
            'title': 'Updated Test Note',
            'text': 'This is an updated test note',
            'slug': 'updated-test-note'
        }

        response = self.author_client.post(self.EDIT_URL, edit_data)
        self.assertRedirects(response, self.SUCCESS_URL)

        updated_note = Note.objects.get(id=self.note.id)
        self._verify_note_attributes(updated_note, edit_data)

    def test_non_author_cannot_edit_note(self):
        response = self.non_author_client.post(self.EDIT_URL, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self._verify_note_attributes(self.note, {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug
        })

    def test_author_can_delete_own_note(self):
        self._attempt_note_deletion()

    def test_non_author_cannot_delete_note(self):
        initial_notes_count = Note.objects.count()
        response = self.non_author_client.post(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_notes_count)

    def _attempt_note_creation(self, form_data, should_fail=False):
        initial_notes_count = Note.objects.count()
        response = self.author_client.post(self.ADD_URL, data=form_data)

        if should_fail:
            self.assertEqual(Note.objects.count(), initial_notes_count)
            self.assertFormError(
                response, 'form', 'slug', form_data['slug'] + WARNING
            )
        else:
            self.assertRedirects(response, self.SUCCESS_URL)
            self.assertEqual(Note.objects.count(), initial_notes_count + 1)
            new_note = Note.objects.get(slug=form_data['slug'])
            self._verify_note_attributes(new_note, form_data)

    def _attempt_note_deletion(self):
        initial_notes_count = Note.objects.count()
        response = self.author_client.post(self.DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), initial_notes_count - 1)

    def _verify_note_attributes(self, note_instance, expected_attributes):
        for attr, expected_value in expected_attributes.items():
            self.assertEqual(getattr(note_instance, attr), expected_value)
