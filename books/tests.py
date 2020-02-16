from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.template import Template, Context
from django.test import TestCase
from django.urls import reverse

from .forms import BookListAddForm
from .models import Author, Book, BookList
from .views import get_recent_books, get_most_read_books, create_book_choices


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


class DashboardViewHelperFunctionsTests(TestCase):
    '''Test dashboard with fixtures with a few data'''

    fixtures = ['fewusers.json', 'booklist_without_ratings']

    def test_most_read_books(self):
        books = get_most_read_books()
        self.assertQuerysetEqual(
            books,
            [
                repr(Book.objects.get(pk=1)),
                repr(Book.objects.get(pk=6)),
                repr(Book.objects.get(pk=10)),
                repr(Book.objects.get(pk=12)),
                repr(Book.objects.get(pk=2)),
            ]
        )

    def test_recently_added_books(self):
        books = get_recent_books()
        self.assertQuerysetEqual(
            books,
            [
                repr(Book.objects.get(pk=12)),
                repr(Book.objects.get(pk=11)),
                repr(Book.objects.get(pk=10)),
                repr(Book.objects.get(pk=9)),
                repr(Book.objects.get(pk=8)),
            ]
        )


class AuthorModelTests(TestCase):

    def setUp(self):
        self.author = Author.objects.create(
            first_name="J. D.", last_name="Salinger")

    def test_string_representation(self):
        self.assertEqual(str(self.author), "J. D. Salinger")

    def test_duplicates(self):
        with self.assertRaises(IntegrityError):
            Author.objects.create(
                first_name="J. D.", last_name="Salinger")


class BookModelTests(TestCase):

    fixtures = ['fewusers.json', 'threebooks.json']

    def setUp(self):
        self.book = Book.objects.get(pk=1)
        self.user = User.objects.get(pk=2)

    def test_string_representation(self):
        self.assertEqual(
            str(self.book),
            "J. D. Salinger: The Catcher in the Rye"
        )

    def test_duplicates(self):
        author = Author.objects.get(pk=1)
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                author=author, title="The Catcher in the Rye",
                first_published=1951
            )

    def test_add_to_booklist_method_with_valid_data(self):
        bl_item, created = self.book.add_to_booklist(self.user)
        self.assertTrue(created)
        self.assertEqual(bl_item.book, self.book)
        self.assertEqual(bl_item.user, self.user)
        self.assertEqual(
            1,
            BookList.objects.filter(user=self.user, book=self.book).count()
        )

    def test_add_to_booklist_method_without_user(self):
        with self.assertRaises(TypeError):
            self.book.add_to_booklist()

    def test_add_to_booklist_method_with_duplicate(self):
        '''Test if the book is already on the user's booklist'''
        BookList.objects.create(user=self.user, book=self.book)
        bl_item, created = self.book.add_to_booklist(self.user)
        self.assertFalse(created)
        self.assertEqual(
            1,
            BookList.objects.filter(user=self.user, book=self.book).count()
        )

    def test_number_of_listings(self):
        '''Test if the number_of_listing property is calculated properly

        Add self.book to 1 list, book2 to zero lists, book3 to 2 list
        '''

        book2 = Book.objects.get(pk=2)
        book3 = Book.objects.get(pk=3)
        user2 = User.objects.get(pk=3)
        self.book.add_to_booklist(self.user)
        book3.add_to_booklist(self.user)
        book3.add_to_booklist(user2)
        self.assertEqual(1, self.book.number_of_listings)
        self.assertEqual(0, book2.number_of_listings)
        self.assertEqual(2, book3.number_of_listings)


class BookListModelTests(TestCase):

    fixtures = ['fewusers.json', 'threebooks.json']

    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.book = Book.objects.get(pk=1)

    def test_string_representation(self):
        book_listed = BookList(user=self.user, book=self.book)
        self.assertEqual(
            str(book_listed),
            "joe lists J. D. Salinger: The Catcher in the Rye")

    def test_duplicates(self):
        BookList.objects.create(user=self.user, book=self.book)
        with self.assertRaises(IntegrityError):
            BookList.objects.create(user=self.user, book=self.book)


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


class BookListAddFormTest(TestCase):

    fixtures = ['fewusers.json', 'threebooks.json']

    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.book = Book.objects.get(pk=1)

    def test_valid_data(self):
        form = BookListAddForm({"book": self.book}, user=self.user)
        self.assertTrue(form.is_valid())
        book_added = form.save()
        self.assertEqual(book_added.user.username, "joe")
        self.assertEqual(book_added.book.title, "The Catcher in the Rye")

    def test_init_without_user(self):
        with self.assertRaises(KeyError):
            BookListAddForm()

    def test_blank_data(self):
        form = BookListAddForm({}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'book': ['This field is required.'],
        })

    def test_book_field(self):
        form = BookListAddForm(user=self.user)
        # book field length should = number of all books + empty value
        self.assertEqual(len(form["book"]), 4)

    def test_existing_books_exluded(self):
        '''
        Books already on the user's list shouldn't be included
        in the book field
        '''
        BookList.objects.create(book=self.book, user=self.user)
        form = BookListAddForm(user=self.user)
        # book field length should =
        # number of all books + empty value - 1 book already in the list
        self.assertEqual(len(form["book"]), 3)
        self.assertNotIn(self.book, form["book"].field.queryset)


class BookListAddViewTests(TestCase):

    fixtures = ['fewusers.json', 'threebooks.json']

    def setUp(self):
        self.user = User.objects.get(pk=2)

    def test_url_logged_out(self):
        response = self.client.get('/my/books/add/')
        self.assertRedirects(
            response,
            f"{reverse('login')}?next=/my/books/add/")

    def test_url_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get('/my/books/add/')
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('books:book_list_add'))
        self.assertTemplateUsed(
            response, template_name='books/book_list_add.html')

    def test_redirect(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('books:book_list_add'),
            {'book': 1}  # book with pk=1
        )
        self.assertRedirects(response, reverse('books:book_list'))


class BookListEditViewTest(TestCase):

    fixtures = ['fewusers.json', 'booklist_without_ratings']

    def setUp(self):
        self.user = User.objects.get(pk=2)

    def test_url_logged_out(self):
        response = self.client.get('/my/books/edit/1/')
        self.assertRedirects(
            response,
            f"{reverse('login')}?next=/my/books/edit/1/")

    def test_url_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get('/my/books/edit/1/')
        self.assertEqual(response.status_code, 200)

    def test_url_logged_in_invalid_id(self):
        self.client.force_login(self.user)
        response = self.client.get('/my/books/edit/5/')
        self.assertEqual(response.status_code, 404)

    def test_template_used(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('books:book_list_edit', kwargs={'pk': 1}))
        self.assertTemplateUsed(
            response, template_name='books/book_list_edit.html')


class BookSearchViewTests(TestCase):

    fixtures = ['fewusers.json', 'threebooks.json']

    def setUp(self):
        self.user = User.objects.get(pk=2)

    def test_url_logged_out(self):
        response = self.client.get('/my/books/search/')
        self.assertRedirects(
            response,
            f"{reverse('login')}?next=/my/books/search/")

    def test_url_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get('/my/books/search/')
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('books:book_search'))
        self.assertTemplateUsed(
            response, template_name='books/book_search.html')

    def test_create_book_choices_helper_function(self):
        results = [
            {
                "cover_edition_key": "OL18",
                "edition_key": ["OL11", "OL18"],
                "author_name": ["Author 1", "Coauthor"],
                "title": "Title 1",
                "first_publish_year": 1968
            },
            {
                "cover_edition_key": "OL71",
                "author_name": ["Author 2", ],
                "title": "Title 2",
                "first_publish_year": 2012
            },
            # this one should be excluded
            {
                "author_name": ["Author 2", ],
                "title": "Title 2",
                "first_publish_year": 2012
            },
        ]
        choices = create_book_choices(results)
        self.assertEqual(
            choices,
            (
                ("OL18", "Author 1: Title 1 (1968)"),
                ("OL71", "Author 2: Title 2 (2012)")
            )
        )


class TestBookCardTag(TestCase):

    fixtures = ['fewusers.json', 'booklist_without_ratings']
    TEMPLATE_NO_LIST = Template("{% load book_tags %} {% book_card book %}")
    TEMPLATE_WITH_LIST = Template(
        "{% load book_tags %} {% booklist_card booklist %}")

    def test_rendering_without_booklist(self):
        book = Book.objects.get(pk=1)
        rendered = self.TEMPLATE_NO_LIST.render(Context({'book': book}))
        self.assertIn(book.title, rendered)

    def test_rendering_booklist_no_overrides(self):
        booklist = BookList.objects.get(pk=1)
        book = booklist.book
        rendered = self.TEMPLATE_WITH_LIST.render(
            Context({'booklist': booklist}))
        self.assertIn(book.title, rendered)

    def test_rendering_booklist_with_overriden_title(self):
        booklist = BookList.objects.get(pk=1)
        booklist.override_title = 'New title'
        booklist.save()
        book = booklist.book
        rendered = self.TEMPLATE_WITH_LIST.render(
            Context({'booklist': booklist}))
        self.assertNotIn(book.title, rendered)
        self.assertIn('New title', rendered)
