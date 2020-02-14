from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from typing import Union

from .forms import BookListAddForm
from .models import Book, BookList


def dashboard(request: HttpRequest) -> HttpResponse:
    ctx = {
        "recent_books": Book.objects.order_by('-added')[:5]
    }
    return render(request, 'books/index.html', ctx)


@login_required
def book_list(request: HttpRequest) -> HttpResponse:
    ctx = {
        "mybooks": BookList.objects.filter(user=request.user)
    }
    return render(request, 'books/book_list.html', ctx)


@login_required
def book_list_add(
        request: HttpRequest) -> Union[HttpResponse, HttpResponseRedirect]:
    form = BookListAddForm(request.POST or None, user=request.user)
    if form.is_valid():
        form.save()
        return redirect('books:book_list')
    return render(request, 'books/book_list_add.html', {'form': form})
