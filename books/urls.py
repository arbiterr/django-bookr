from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('my/books/', views.book_list, name='book_list'),
    path('my/books/add/', views.book_list_add, name='book_list_add'),
    path(
        'my/books/edit/<int:pk>/', views.book_list_edit,
        name='book_list_edit'
    ),
    path(
        'my/books/delete/<int:pk>/', views.book_list_delete,
        name='book_list_delete'
    ),
    path('my/books/search/', views.book_search, name='book_search'),
    path('my/books/rate/', views.book_rate, name='book_rate'),
]
