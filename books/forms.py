from django import forms

from .models import BookList, Book


class BookListAddForm(forms.ModelForm):
    '''Form for adding books to the user's list from the existing books'''

    class Meta:
        model = BookList
        fields = ('book',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['book'].queryset = Book.objects.exclude(
            booklist__user=self.user)

    def save(self):
        book = super().save(commit=False)
        book.user = self.user
        book.save()
        return book
