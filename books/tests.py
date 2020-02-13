from django.test import TestCase
from django.urls import reverse

from .models import Author, Book


class DashboardViewEmptyDBTests(TestCase):
    '''Test dashboard without fixtures'''

    def setUp(self):
        self.author = Author.objects.create(
            first_name="J. D.", last_name="Salinger")

    def test_url(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_invalid_url(self):
        response = self.client.get('/blaba2198/')
        self.assertEqual(response.status_code, 404)

    def test_template_used(self):
        response = self.client.get(reverse('books:dashboard'))
        self.assertTemplateUsed(response, template_name='books/index.html')

    def test_no_books(self):
        response = self.client.get(reverse('books:dashboard'))
        self.assertContains(response, 'No books rated yet.')
        self.assertContains(response, 'No books read yet.')
        self.assertContains(response, 'No books added yet.')


class DashboardViewSmallDBTests(TestCase):
    '''Test dashboard with fixtures with a few data'''

    fixtures = ['threebooks.json']

    def test_recently_added_books(self):
        response = self.client.get(reverse('books:dashboard'))
        self.assertQuerysetEqual(
            response.context['recent_books'],
            [
                repr(Book.objects.get(pk=3)),
                repr(Book.objects.get(pk=2)),
                repr(Book.objects.get(pk=1))
            ]
        )


class AuthorModelTests(TestCase):

    def test_string_representation(self):
        author = Author(first_name="J. D.", last_name="Salinger")
        self.assertEqual(str(author), "Salinger, J. D.")


class BookModelTests(TestCase):

    def setUp(self):
        self.author = Author.objects.create(
            first_name="J. D.", last_name="Salinger")

    def test_string_representation(self):
        book = Book(
            author=self.author,
            title="The Catcher in the Rye",
            first_published=1951
        )
        self.assertEqual(str(book), "Salinger, J. D.: The Catcher in the Rye")
