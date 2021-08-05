from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
import uuid


# Create your models here.
class Genre(models.Model):
	""" Model representing the books genre """
	name = models.CharField(max_length=200, help_text="Enter book genre (e.g. Science Fiction)")

	def get_absolute_url(self):
		return reverse('genre-detail', args=[str(self.id)])

	def __str__(self):
		""" String for representing Model object """
		return self.name



class Language(models.Model):
	name = models.CharField(max_length=100, help_text='Enter original language of the book (e.g. English)')

	def __str__(self):
		return self.name


class Book(models.Model):
	""" Model representing the Books """
	title = models.CharField(max_length=200)
	summary = models.TextField()
	isbn = models.CharField("ISBN", max_length=13, unique=True,
							help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
	author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
	genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
	language = models.ManyToManyField(Language, help_text="Select a language for this book")

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		"""Returns the url to access a detail record for this book."""
		return reverse('book-detail', args=[str(self.id)])

	def display_genre(self):
		"""Create a string for the Genre. This is required to display genre in Admin."""
		return ", ".join(genre.name for genre in self.genre.all())

	def display_language(self):
		"""Create a string for the Language. This is required to display language in Admin."""
		return ", ".join(lang.name for lang in self.language.all())

	display_genre.short_description = 'Genre'
	display_language.short_description = 'Language'



class BookInstance(models.Model):
	""" Model representing a specific copy of a book (i.e. can be borrowed from the library) """
	LOAN_STATUS = (
		('m', 'Maintenance'),
		('o', 'On loan'),
		('a', 'Available'),
		('r', 'Reserved'),
	)

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
	book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
	imprint = models.CharField(max_length=200)
	due_back = models.DateField(null=True, blank=True)

	status = models.CharField(
		max_length = 1,
		choices = LOAN_STATUS,
		blank = True,
		default = 'm',
		help_text = 'Book Availablity',
	)

	borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		ordering = ['due_back']
		permissions = (('can_mark_returned', 'Set book as returned'),)

	@property
	def is_overdue(self):
		if self.due_back and date.today() > self.due_back:
			return True
		return False

	def __str__(self):
		return f"{self.id} ({self.book.title})"



class Author(models.Model):
	""" Model representing the Authors """
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	date_of_birth = models.DateField(null=True, blank=True)
	date_of_death = models.DateField('died', null=True, blank=True)

	class Meta:
		ordering = ['first_name','last_name']

	def __str__(self):
		return f"{self.first_name} {self.last_name}"

	def get_absolute_url(self):
		return reverse('author-detail', args=[str(self.id)])


class UserToken(models.Model):
	""" Adds extra field to default user model """
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	user_token = models.UUIDField(default=uuid.uuid4, 
								  help_text='Unique token for this user',
								  verbose_name='Token',
								  unique=True)

	def __str__(self):
		return f"{self.user_token}"
