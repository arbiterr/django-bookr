from django.conf import settings
from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    first_published = models.IntegerField('year of first publication')
    added = models.DateTimeField(
        'originally added to the database', auto_now_add=True)
    cover = models.URLField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.author}: {self.title}'

    def add_to_booklist(self, user):
        return self.booklist_set.get_or_create(user=user)


class BookList(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    override_title = models.CharField(max_length=50, blank=True)
    override_author = models.CharField(max_length=50, blank=True)
    override_year = models.IntegerField(
        'override year of first publication', null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} lists {self.book}'
