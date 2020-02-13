from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f'{self.last_name}, {self.first_name}'


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    first_published = models.IntegerField('year of first publication')
    added = models.DateTimeField(
        'originally added to the database', auto_now_add=True)
    cover = models.URLField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f'{self.author}: {self.title}'
