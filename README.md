# Django-Bookr

This project allows users to track and rate the books they've read.

## Features

### Account management

* [x] Users can create an account
* [x] Users can log in
* [x] Users can reset their password

### Book list

* [x] Users can view their own list of books
* [x] Users can add books to their list
* [x] Users can update the books on their list
* [x] Users can remove books from their list
* [x] Users can rate their books on a scale of 1 to 5
* [x] A list of books can only be viewed by its owner

### Dashboard

* [x] The dashboard displays the top 5 highest rated books
* [x] The dashboard displays the top 5 most read books
* [x] The dashboard displays the 5 books added most recently
* [x] Both visitors and authenticated users can view the dashboard

### Extra

* [x] If a book is not in the database yet, users can search for it on OpenLibrary

## Demo

https://django-bookr.herokuapp.com/

## Running locally

1. Clone/download the repository
2. Create your virtual environment
3. Edit `bookr/settings/local.py` with your database settings
4. Run:
```
pip install -r requirements.txt
python manage.py migrate  --settings=bookr.settings.local
python manage.py runserver --settings=bookr.settings.local
```
5. Optionally create a superuser or load any of the fixtures in `bookr/fixtures/`
