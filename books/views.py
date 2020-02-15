from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import requests

from .forms import BookListAddForm, SearchResultsForm
from .models import Author, Book, BookList


def dashboard(request):
    ctx = {
        "recent_books": Book.objects.order_by('-added')[:5]
    }
    return render(request, 'books/index.html', ctx)


@login_required
def book_list(request):
    ctx = {
        "mybooks": BookList.objects.filter(user=request.user)
    }
    return render(request, 'books/book_list.html', ctx)


@login_required
def book_list_add(request):
    form = BookListAddForm(request.POST or None, user=request.user)
    if form.is_valid():
        form.save()
        return redirect('books:book_list')
    return render(request, 'books/book_list_add.html', {'form': form})


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
