from django.conf import settings
from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['first_name', 'last_name'], name='unique_author')
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    first_published = models.IntegerField('year of first publication')
    added = models.DateTimeField(
        'originally added to the database', auto_now_add=True)
    cover = models.URLField(max_length=100, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title', 'first_published'],
                name='unique_book')
        ]

    def __str__(self):
        return f'{self.author}: {self.title}'

    @property
    def number_of_listings(self):
        '''Calculates how many times was a book listed by users'''
        self._number_of_listings = self.booklist_set.count()
        return self._number_of_listings

    @property
    def average_rating(self):
        '''Calculates average rating'''
        self._average_rating = self.booklist_set.aggregate(
            models.Avg('rating'))['rating__avg']
        return self._average_rating

    def add_to_booklist(self, user, rating=None):
        return self.booklist_set.get_or_create(user=user, rating=rating)


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
    override_cover = models.URLField(max_length=100, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'book'], name='unique_booklist')
        ]

    def __str__(self):
        return f'{self.user.username} lists {self.book}'

    def get_title(self):
        return self.override_title if self.override_title else self.book.title

    def get_author(self):
        if self.override_author:
            return self.override_author
        else:
            return self.book.author

    def get_cover(self):
        return self.override_cover if self.override_cover else self.book.cover

    def get_year(self):
        if self.override_year:
            return self.override_year
        else:
            return self.book.first_published
