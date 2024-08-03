from notes.forms import NoteForm
from notes.tests.conftest import TestNote


class TestNotesContent(TestNote):

    def test_note_visibility_for_author_and_non_author(self):
        response_author = self.author_client.get(self.LIST_URL)
        response_non_author = self.non_author_client.get(self.LIST_URL)

        self.assertIn(self.note, response_author.context['object_list'])
        self.assertNotIn(self.note, response_non_author.context['object_list'])

    def test_form_is_present_on_add_and_edit_pages(self):
        for url in [self.ADD_URL, self.EDIT_URL]:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
