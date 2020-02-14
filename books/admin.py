from django.contrib import admin

from .models import Author, Book, BookList


class BookAdmin(admin.ModelAdmin):
    model = Book
    list_display = ('author', 'title', 'first_published', 'added')
    list_filter = ['author']
    search_fields = ['title']


class BookListAdmin(admin.ModelAdmin):
    model = BookList
    list_display = ('user', 'book', 'rating', 'added', 'updated')
    list_filter = ['user', 'book']


admin.site.register(Author)
admin.site.register(Book, BookAdmin)
admin.site.register(BookList, BookListAdmin)
