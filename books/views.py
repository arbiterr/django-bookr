from django.db.models import Avg, Count
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.forms import modelform_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
import requests

from .forms import BookListAddForm, SearchResultsForm
from .models import Author, Book, BookList

# Helper functions #


def get_most_read_books():
    '''Get books added on the most lists

    If two or more books are on the same number of lists, the oldest book
    gets higher rank'''

    return Book.objects.annotate(
        num_lists=Count('booklist')).order_by('-num_lists', 'added')[:5]


def get_recent_books():
    '''Get 5 most recently added books to the db'''
    return Book.objects.order_by('-added')[:5]


def get_top_rated_books():
    '''Get the top 5 books with highest average rating

    If two or more books has the same average rating, then the next criteria is
    number of listings, then time added (oldest higher rank)
    '''

    return Book.objects.annotate(
        num_lists=Count('booklist'),
        avg_rating=Avg('booklist__rating')
    ).order_by('-avg_rating', '-num_lists', 'added')[:5]


def create_book_choices(results):
    '''
    Helper function to create choices for the SearchResultsForm

    Params:
        results(list): list of books found on OpenLibrary
    Returns:
        choices(tuple): tuple of tuples for the forms.ChoiceField
    '''

    choices = tuple(
        (
            b["cover_edition_key"] if "cover_edition_key" in b
            else b["edition_key"][0],
            (
                f'{b["author_name"][0]}: {b["title"]} '
                f'({b["first_publish_year"]})'
            )
        ) for b in results
        # only include results with all required attributes
        if set(("cover_edition_key", "author_name", "title",
               "first_publish_year")) <= set(b)
    )
    return choices


# Views #

def dashboard(request):
    ctx = {
        "most_read_books": get_most_read_books(),
        "recent_books": get_recent_books(),
        "top_books": get_top_rated_books()
    }
    return render(request, 'books/index.html', ctx)


@login_required
def book_list(request):
    ctx = {
        "mybooks": BookList.objects.filter(
            user=request.user).order_by(
                'book__author__last_name', 'book__title')
    }
    return render(request, 'books/book_list.html', ctx)


@login_required
def book_list_add(request):
    form = BookListAddForm(request.POST or None, user=request.user)
    if form.is_valid():
        form.save()
        return redirect('books:book_list')
    return render(request, 'books/book_list_add.html', {'form': form})


@login_required
def book_list_edit(request, pk):
    bl_item = get_object_or_404(BookList, pk=pk, user=request.user)
    book = bl_item.book
    HELP_TEXT_TRUNK = 'Originally: '
    BookListEditForm = modelform_factory(
        BookList,
        fields=(
            'override_author', 'override_title',
            'override_year', 'override_cover'
        ),
        help_texts={
            'override_author': HELP_TEXT_TRUNK+str(book.author),
            'override_title': HELP_TEXT_TRUNK+book.title,
            'override_year': HELP_TEXT_TRUNK+str(book.first_published),
            'override_cover': HELP_TEXT_TRUNK+book.cover
        }
    )
    form = BookListEditForm(request.POST or None, instance=bl_item)
    if form.is_valid():
        form.save()
        return redirect('books:book_list')
    return render(request, 'books/book_list_edit.html', {'form': form})


@login_required
def book_list_delete(request, pk):
    '''Remove a book from user's booklist'''
    # TODO: refactor this to work with DELETE or POST method
    bl_item = get_object_or_404(BookList, pk=pk, user=request.user)
    bl_item.delete()
    return redirect('books:book_list')


@login_required
def book_search(request):
    '''Search OpenLibrary then use results as input for a create book form'''
    if request. method == "GET":
        q = request.GET.get('q', '')
        if q:
            # TODO: handle exceptions
            # TODO: test with mocks
            response = requests.get(
                "https://openlibrary.org/search.json",
                params={'q': q}
            )
            results = response.json()['docs'][:10]
            book_choices = create_book_choices(results)
            form = SearchResultsForm(book_choices=book_choices)
        else:
            form = None
        return render(request, 'books/book_search.html', {'form': form})
    elif request. method == "POST":
        olid = request.POST.get("book", '')
        if olid:
            # TODO: handle exceptions
            # TODO: test with mocks
            response = requests.get(
                "https://openlibrary.org/api/books",
                params={'bibkeys': olid, 'format': 'json', 'jscmd': 'data'}
            )
            result = response.json()[olid]
            # assume that the last word is the last name
            first_name, last_name = result['authors'][0]['name'].rsplit(' ', 1)
            # some pub dates are full dates, some just years
            # if it's a full date, than extract the year from the full date
            if ' ' in result['publish_date']:
                pub_year = int(result['publish_date'].rsplit(' ', 1)[1])
            else:
                pub_year = int(result['publish_date'])
            # check if the author in already the db
            # if not, add it
            author, a_created = Author.objects.get_or_create(
                first_name=first_name, last_name=last_name)
            # check if we book is already in the db
            # if not, add it
            book, b_created = Book.objects.get_or_create(
                author=author, title=result['title'], first_published=pub_year)
            if b_created and 'cover' in result:
                book.cover = result['cover']['medium']
                book.save()
            book.add_to_booklist(request.user)
        return redirect('books:book_list')


@require_POST
@login_required
def book_rate(request):
    booklist_id = int(request.POST.get('booklist_id', 0))
    new_rating = int(request.POST.get('rating', 0))
    if booklist_id and new_rating in range(1, 6):
        bl_item = get_object_or_404(
            BookList, pk=booklist_id, user=request.user)
        bl_item.rating = new_rating
        bl_item.save()
        return JsonResponse({
            'booklist_id': bl_item.id, 'rating': bl_item.rating
        })
    else:
        return JsonResponse({}, status=404)
