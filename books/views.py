from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Book


def dashboard(request: HttpRequest) -> HttpResponse:
    ctx = {
        "recent_books": Book.objects.order_by('-added')[:5]
    }
    return render(request, 'books/index.html', ctx)
