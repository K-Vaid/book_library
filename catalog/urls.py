from django.urls import path

from . import views


# General pages
urlpatterns = [
	path("", views.index, name="index"),
	path("accounts/signup", views.UserRegister.as_view(), name="member-signup"),
	path("accounts/profile/<int:pk>", views.UserProfile.as_view(), name="member-profile"),
	path("accounts/<int:uid>/verify/<uuid:token>", views.verifyMemberToken, name="member-verify"),
]


# Books related
urlpatterns += [
	path("books/", views.BookListView.as_view(), name="books"),
	path("book/<int:pk>", views.BookDetailView.as_view(), name="book-detail"),
	path("book/create/", views.BookCreate.as_view(), name="book-create"),
	path("book/<int:pk>/update/", views.BookUpdate.as_view(), name="book-update"),
	path("book/<int:pk>/delete/", views.BookDelete.as_view(), name="book-delete"),
]

# Author related
urlpatterns += [
	path("authors/", views.AuthorListView.as_view(), name="authors"),
	path("author/<int:pk>", views.AuthorDetailView.as_view(), name="author-detail"),
	path("author/create/", views.AuthorCreate.as_view(), name="author-create"),
	path("author/<int:pk>/update/", views.AuthorUpdate.as_view(), name="author-update"),
	path("author/<int:pk>/delete/", views.AuthorDelete.as_view(), name="author-delete"),
]

# Genre related
urlpatterns += [
	path("genres/", views.GenresListView.as_view(), name="genres"),
	path("genres/<int:pk>", views.genre_details, name="genre-detail"),
]

# User related (functional) [ member and staff]
urlpatterns += [
	path("mybooks/", views.BorrowerListView.as_view(), name="my-borrowed"),
	path("book/<uuid:pk>/borrow/", views.BorrowBook.as_view(), name="borrow-book"),
	path("book/<uuid:pk>/return/", views.return_book, name="return-book"),
	path("borrowed/", views.LibrarianListView.as_view(), name="all-borrowed"),
	path("book/<uuid:pk>/renew/", views.renew_book_librarian, name="renew-book-librarian"),
]