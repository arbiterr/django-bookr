from django import template

register = template.Library()


@register.inclusion_tag('books/_card_book.html')
def book_card(book):
    return {
        'cover': book.cover, 'author': book.author, 'title': book.title,
        'number_of_listings': book.number_of_listings,
        'avg_rating': book.average_rating
        }


@register.inclusion_tag('books/_card_booklist.html')
def booklist_card(booklist):
    return {
        'cover': booklist.get_cover(), 'author': booklist.get_author(),
        'title': booklist.get_title(), 'booklist_id': booklist.id,
        'rating': booklist.rating
        }
