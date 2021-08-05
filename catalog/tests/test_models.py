from django.test import TestCase

from catalog.models import Author

# Create your tests here.
class AuthorModelTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# Set up non-modified objects used by all test methods
		Author.objects.create(first_name="Test", last_name="Author")

	def test_first_name_label(self):
		author = Author.objects.get(id=1)
		field_name = author._meta.get_field("first_name").verbose_name
		self.assertEqual(field_name, "first name")

	def test_first_name_max_length(self):
	    author = Author.objects.get(id=1)
	    max_length = author._meta.get_field('first_name').max_length
	    self.assertEqual(max_length, 100)

	def test_date_of_death_label(self):
		author = Author.objects.get(id=1)
		field_name = author._meta.get_field("date_of_death").verbose_name
		self.assertEqual(field_name, "died")


	def test_object_name_is_first_name_comma_last_name(self):
		author = Author.objects.get(id=1)
		expected_name = f"{author.first_name} {author.last_name}"
		self.assertEqual(str(author), expected_name)

	def test_get_absolute_url(self):
		author = Author.objects.get(id=1)
		expected_name = f"{author.first_name}, {author.last_name}"
		self.assertEqual(author.get_absolute_url(), "/catalog/author/1")

	