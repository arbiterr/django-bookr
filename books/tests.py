from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Author, Book, BookList


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


class BookListModelTests(TestCase):

    fixtures = ['fewusers.json', 'threebooks.json']

    def test_string_representation(self):
        user = User.objects.get(pk=2)
        book = Book.objects.get(pk=1)
        book_listed = BookList(user=user, book=book)
        self.assertEqual(
            str(book_listed),
            "joe lists Salinger, J. D.: The Catcher in the Rye")


class BookListViewTests(TestCase):

    fixtures = ['fewusers.json', 'threebooks.json']

    def setUp(self):
        self.user = User.objects.get(pk=2)

    def test_url_logged_out(self):
        response = self.client.get('/my/books/')
        self.assertRedirects(
            response,
            f"{reverse('login')}?next=/my/books/")

    def test_url_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get('/my/books/')
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('books:book_list'))
        self.assertTemplateUsed(response, template_name='books/book_list.html')

    def test_empty_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('books:book_list'))
        self.assertContains(response, 'No books on your list yet.')

    def test_one_book_on_the_list(self):
        book = Book.objects.get(pk=1)
        BookList.objects.create(user=self.user, book=book)
        self.client.force_login(self.user)
        response = self.client.get(reverse('books:book_list'))
        self.assertContains(response, 'The Catcher in the Rye')

    def test_three_books_on_the_list(self):
        for book in Book.objects.all():
            BookList.objects.create(user=self.user, book=book)
        self.client.force_login(self.user)
        response = self.client.get(reverse('books:book_list'))
        self.assertContains(response, 'The Catcher in the Rye')
        self.assertContains(response, 'Nine stories')
        self.assertContains(response, 'Franny and Zooey')
