from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, 'books/index.html', {})
