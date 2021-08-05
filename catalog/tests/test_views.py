import datetime
import uuid


from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

# Required to grant the permission needed to set a book as returned.
from django.contrib.auth.models import Permission 

from catalog.models import Author, BookInstance, Book, Genre, Language


# Create your tests here.
class AuthorListViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create 13 authors for pagination test
		no_of_authors = 13

		for author_id in range(no_of_authors):
			Author.objects.create(
				first_name = f"Dummy {author_id}",
				last_name = f"Author {author_id}"
			)

	def test_view_url_exists_at_desired_location(self):
		response = self.client.get("/catalog/authors/")
		self.assertEqual(response.status_code, 200)

	def test_view_url_accessible_by_name(self):
		response = self.client.get(reverse('authors'))
		self.assertEqual(response.status_code, 200)

	def test_view_uses_correct_template(self):
		response = self.client.get(reverse('authors'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, "author_list.html")

	def test_pagination_is_ten(self):
		response = self.client.get(reverse('authors'))
		self.assertEqual(response.status_code, 200)
		self.assertTrue("is_paginated" in response.context)
		self.assertTrue(response.context["is_paginated"] == True)
		self.assertEqual(len(response.context["author_list"]), 10)

	def test_lists_all_authors(self):
		response = self.client.get(reverse('authors')+"?page=2")
		self.assertEqual(response.status_code, 200)
		self.assertTrue("is_paginated" in response.context)
		self.assertTrue(response.context["is_paginated"] == True)
		self.assertEqual(len(response.context["author_list"]), 3)



class BorrowerListViewTest(TestCase):
	def setUp(self):
		# create two users
		test_user1 = User.objects.create_user(
			username = "test_user1",
			password = "j123nkhahKA#snjsn"
		)
		test_user2 = User.objects.create_user(
			username = "test_user2",
			password = "j14Aj34jkad+snjsn"
		)

		test_user1.save()
		test_user2.save()

		# create a Book
		test_author = Author.objects.create(first_name="John", last_name="Rambo")
		test_genre = Genre.objects.create(name="Action")
		test_language = Language.objects.create(name="Spainsh")
		test_book = Book.objects.create(
			title = "The django testing",
			summary = "this is to test django views",
			author = test_author,
			isbn = "123456789"
		)

		# create genre as a post step
		genres_for_books = Genre.objects.all()
		test_book.genre.set(genres_for_books)
		test_book.language.set(Language.objects.all())
		test_book.save()

		# create 30 bookinstance objects
		no_of_book_copies = 30
		for copy in range(no_of_book_copies):
			book = test_book
			borrower = test_user2 if copy % 2 else test_user1
			return_date = timezone.localtime() + datetime.timedelta(days=copy%5)

			test_instance = BookInstance.objects.create(
				book = book,
				status = "m",
				imprint = "Great Pubmications",
				borrower = borrower,
				due_back = return_date
			)


	def test_redirect_if_not_logged_in(self):
		response = self.client.get(reverse('my-borrowed'))
		self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')

	def test_logged_in_uses_correct_template(self):
		login = self.client.login(username="test_user1", password="j123nkhahKA#snjsn")
		response = self.client.get(reverse('my-borrowed'))

		# check correct user logged in
		self.assertEqual(str(response.context["user"]), "test_user1")
		self.assertEqual(response.status_code, 200)

		# check for correct template
		self.assertTemplateUsed(response, "borrower_list_view.html")


	def test_only_borrowed_books_in_list(self):
		login = self.client.login(username="test_user1", password="j123nkhahKA#snjsn")
		response = self.client.get(reverse('my-borrowed'))

		# check correct user logged in
		self.assertEqual(str(response.context["user"]), "test_user1")
		self.assertEqual(response.status_code, 200)

		# check book list initially
		self.assertTrue("borrowed_books" in response.context)
		self.assertEqual(len(response.context["borrowed_books"]),0)

		books = BookInstance.objects.all()[:10]

		for book in books:
			book.status = "o"
			book.save()

		response = self.client.get(reverse('my-borrowed'))
		# check correct user logged in
		self.assertEqual(str(response.context["user"]), "test_user1")
		self.assertEqual(response.status_code, 200)

		# check book list initially
		self.assertTrue("borrowed_books" in response.context)

		# confirm all books belong to test_user1 and are on loan
		for book in response.context["borrowed_books"]:
			self.assertEqual(response.context["user"], book.borrower)
			self.assertEqual(book.status, "o")


	def test_pages_ordered_by_due_date(self):
		books = BookInstance.objects.all()

		for book in books:
			book.status = "o"
			book.save()

		login = self.client.login(username="test_user1", password="j123nkhahKA#snjsn")
		response = self.client.get(reverse('my-borrowed'))

		# check correct user logged in
		self.assertEqual(str(response.context["user"]), "test_user1")
		self.assertEqual(response.status_code, 200)

		# check book list initially
		self.assertEqual(len(response.context["borrowed_books"]),10)

		last_date = 0
		for book in response.context['borrowed_books']:
			if last_date == 0:
			    last_date = book.due_back
			else:
			    self.assertTrue(last_date <= book.due_back)
			    last_date = book.due_back


class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.language.set(Language.objects.all()) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )


    def test_redirect_if_not_logged_in(self):
    	response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
    	# Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
    	self.assertEqual(response.status_code, 302)
    	self.assertTrue(response.url.startswith('/accounts/login/'))
    
    def test_forbidden_if_logged_in_but_not_correct_permission(self):
    	login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
    	response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
    	self.assertEqual(response.status_code, 403)
    
    def test_logged_in_with_permission_borrowed_book(self):
    	login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
    	response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk}))
    	# Check that it lets us login - this is our book and we have the right permissions.
    	self.assertEqual(response.status_code, 200)
    
    def test_logged_in_with_permission_another_users_borrowed_book(self):
    	login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
    	response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
    	# Check that it lets us login. We're a librarian, so we can view any users book
    	self.assertEqual(response.status_code, 200)
    
    def test_HTTP404_for_invalid_book_if_logged_in(self):
    	# unlikely UID to match our bookinstance!
    	test_uid = uuid.uuid4()
    	login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
    	response = self.client.get(reverse('renew-book-librarian', kwargs={'pk':test_uid}))
    	self.assertEqual(response.status_code, 404)
    
    def test_uses_correct_template(self):
    	login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
    	response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
    	self.assertEqual(response.status_code, 200)
    	# Check we used correct template
    	self.assertTemplateUsed(response, 'book_renew_librarian.html')
    
    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
    	login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
    	response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
    	self.assertEqual(response.status_code, 200)
    	date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
    	self.assertEqual(response.context['form'].initial['renewal_date'], date_3_weeks_in_future)