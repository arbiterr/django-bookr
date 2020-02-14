from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

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
