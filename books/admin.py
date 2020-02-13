from django.contrib import admin

from .models import Author, Book


class BookAdmin(admin.ModelAdmin):
    model = Book
    list_display = ('author', 'title', 'first_published', 'added')
    list_filter = ['author']
    search_fields = ['title']


admin.site.register(Author)
admin.site.register(Book, BookAdmin)
