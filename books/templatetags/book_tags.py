from django import template

register = template.Library()


@register.inclusion_tag('books/_book_card.html')
def book_card(book):
    return {'book': book}
