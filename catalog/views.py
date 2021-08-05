import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django import forms as dj_forms
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

from . import models, forms


#####################
# Home/Landing Page #
#####################

def index(request):
	""" View function for the home page of site """

	# Generate counts of some main objects
	num_books = models.Book.objects.count()
	num_instances = models.BookInstance.objects.count()
	num_authors = models.Author.objects.count()
	num_genres = models.Genre.objects.count()

	# Available books with status 'a'
	num_instances_available = models.BookInstance.objects.filter(status__exact='a').count()

	# Books that contains 'love' word
	num_word_books = models.Book.objects.filter(summary__icontains='love').count()

	# Number of total visits
	num_visits = request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits + 1

	context = {
		'num_books' : num_books,
		'num_instances' : num_instances,
		'num_authors' : num_authors,
		'num_instances_available' : num_instances_available,
		'num_word_books' : num_word_books,
		'num_genres' : num_genres,
		'num_visits' : num_visits
	}

	return render(request, "index.html", context=context)


#####################
# User Registration #
#####################

class UserRegister(UserPassesTestMixin, CreateView):
	model = User
	form_class = forms.SignupForm
	success_url = reverse_lazy('login')

	def test_func(self):
		return not self.request.user.is_authenticated

	def handle_no_permission(self):
		return HttpResponseRedirect(reverse('member-profile', args=[str(self.request.user.pk)]))

	def form_valid(self, form, **kwargs):
		messages.success(self.request, "Sign Up Successful! Please verify your Email before login.")

		form.instance.is_active = 0
		response =  super(UserRegister, self).form_valid(form)

		user_group = Group.objects.get(name="Library Members")
		self.object.groups.add(user_group)

		member_token = self.object.usertoken.user_token
		site_url = f"{self.request.scheme}://{self.request.get_host()}"
		verify_link = reverse("member-verify", args=[str(member_token), str(self.object.id)])
		send_mail(
			subject = "New Member Signup: Email confirmation.",
			message = f"Welcome {self.object.username}, please click the link below \
						to confirm your email address.{site_url}{verify_link}",
			from_email = "lib_admin@mojo.com",
			recipient_list = [self.object.email]
		)

		return response
		

def verifyMemberToken(request, uid, token):
	token_instance = get_object_or_404(models.UserToken, user_token=token)
	user_instance = get_object_or_404(User, id=uid)
	if token_instance and user_instance:
		user_id = token_instance.user.id
		print(user_id)
		if user_id == user_instance.id:
			user_instance.is_active = 1
			user_instance.save()
			messages.success(request,"Email Verified Sucessfully!")
			return HttpResponseRedirect(reverse("login"))
		messages.error(request, "Verification Failed. Invalid Token recieved for the member.")
		return HttpResponseRedirect(reverse("index"))


class UserProfile(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = User
	form_class = forms.ProfileForm

	def form_valid(self, form, **kwargs):
		messages.success(self.request, "Profile Updated Successfully!")
		self.success_url = reverse_lazy('member-profile', args=[str(self.request.user.pk)])
		return super().form_valid(form)

	def form_invalid(self, form, **kwargs):
		messages.error(self.request, "Profile Updation Failed!")
		self.success_url = reverse_lazy('member-profile', args=[str(self.request.user.pk)])
		return super().form_invalid(form)

	def test_func(self):
		return self.request.user.pk == int(self.kwargs['pk'])

	def handle_no_permission(self):
		if self.request.user.is_authenticated:
			messages.error(self.request, "Forbidden Request. Not allowed to acccess other people's profile.")
			return HttpResponseRedirect(reverse('member-profile', args=[str(self.request.user.pk)]))
		else:
			return HttpResponseRedirect(reverse("login"))



#################################
# Generic List and Detail pages #
#################################

class BookListView(generic.ListView):
	model = models.Book
	context_object_name = "library_books"
	template_name = "book_list.html"
	# queryset = models.Book.objects.filter(title__icontains='war')
	paginate_by = 5

	def get_queryset(self):
		query = self.request.GET.get('q')
		if query and query == "available":
			object_list = self.model.objects.filter(bookinstance__status="a").distinct()
			self.paginate_by = ""
		else:
			object_list = self.model.objects.all()
		return object_list

	def get_context_data(self, **kwargs):
		context = super(BookListView, self).get_context_data(**kwargs)
		context['book_type'] = "Latest Books"
		return context


class BookDetailView(generic.DetailView):
	model = models.Book
	template_name = 'book_detail.html'



class AuthorListView(generic.ListView):
	model = models.Author
	template_name = "author_list.html"
	paginate_by = 10


class AuthorDetailView(generic.DetailView):
	model = models.Author
	template_name = "author_detail.html"


class BorrowerListView(LoginRequiredMixin, generic.ListView):
	"""Generic class-based view listing books on loan to current user."""
	model = models.BookInstance
	template_name = 'borrower_list_view.html'
	context_object_name = 'borrowed_books'
	paginate_by = 10

	def get_queryset(self):
		return models.BookInstance.objects.filter(
					borrower = self.request.user
				).filter(
					status__exact='o'
				).order_by(
					'due_back'
				)


class LibrarianListView(PermissionRequiredMixin, generic.ListView):
	""" View for Librarians to manage borrowed books """
	permission_required = 'catalog.can_mark_returned'
	model = models.BookInstance
	template_name = 'librarian_records.html'
	context_object_name = 'librarian_records'

	def get_queryset(self):
		return models.BookInstance.objects.filter(
					status__exact='o'
				).order_by(
					'due_back'
				)


class GenresListView(generic.ListView):
	model = models.Genre
	template_name = 'genre_list.html'
	paginate_by = 10


def genre_details(request, pk):
	genre = get_object_or_404(models.Genre, id=pk)

	if genre:
		books = models.Book.objects.filter(
				genre = pk
			)

		context = {
			'book_genre' : books,
			'genre' : genre
		}

		return render(request, "genre_detail.html", context=context)

	return redirect('index')



##############################
# Librarian (staff) accesses #
##############################

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
	book_instance = get_object_or_404(models.BookInstance, pk=pk)

	if request.method == "POST":
		form = forms.RenewBookForm(request.POST)

		if form.is_valid():
			book_instance.due_back = form.cleaned_data['renewal_date']
			book_instance.save()

			return HttpResponseRedirect(reverse('all-borrowed'))

	else:
		proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		form = forms.RenewBookForm(initial={"renewal_date":proposed_renewal_date})

	context = {
		"form" : form,
		"book_instance" : book_instance,
	}

	return render(request, "book_renew_librarian.html", context=context)


##################################
# Authors Create, Update, Delete #
##################################

class AuthorCreate(PermissionRequiredMixin, CreateView):
	permission_required = "catalog.can_mark_returned"
	model = models.Author
	fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
	# initial = {"date_of_death" : "20/06/2021"}

	def get_form(self, form_class=None):
		if form_class is None:
			form_class = self.get_form_class()

		form = super(AuthorCreate, self).get_form(form_class)
		form.fields['date_of_birth'].widget = dj_forms.TextInput(attrs={"placeholder":" yyyy-mm-dd"})
		form.fields['date_of_death'].widget = dj_forms.TextInput(attrs={"placeholder":" yyyy-mm-dd"})

		return form

	def form_valid(self, form, **kwargs):
		dob = form.instance.date_of_birth
		dod = form.instance.date_of_death

		if dob > dod:
			form.add_error(None, 
				ValidationError(_("Invalid dates - Date of Birth can't be greater than Date of Death."))
			)
			return super().form_invalid(form)
		return super().form_valid(form)


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
	permission_required = "catalog.can_mark_returned"
	model = models.Author
	fields = '__all__'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
	permission_required = "catalog.can_mark_returned"
	model = models.Author
	success_url = reverse_lazy('authors')



################################
# Books Create, Update, Delete #
################################

class BookCreate(PermissionRequiredMixin, CreateView):
	permission_required = "catalog.can_mark_returned"
	model = models.Book
	fields = "__all__"

class BookUpdate(PermissionRequiredMixin, UpdateView):
	permission_required = "catalog.can_mark_returned"
	model = models.Book
	fields = "__all__"

class BookDelete(PermissionRequiredMixin, DeleteView):
	permission_required = "catalog.can_mark_returned"
	model = models.Book
	success_url = reverse_lazy("books")



#####################################
# Borrow/Return Book (BookInstance) #
#####################################

class BorrowBook(LoginRequiredMixin, UpdateView):
	model = models.BookInstance
	fields = ['book', 'imprint', 'due_back']
	initial = {"due_back":datetime.date.today() + datetime.timedelta(weeks=3)}
	success_url = reverse_lazy('my-borrowed')

	def get_form(self, form_class=None):
		if form_class is None:
			form_class = self.get_form_class()

		form = super(BorrowBook, self).get_form(form_class)
		form.fields['book'].widget = dj_forms.TextInput(attrs={"type":"hidden"})
		form.fields['imprint'].widget = dj_forms.TextInput(attrs={"type":"hidden"})
		form.fields['due_back'].widget = dj_forms.TextInput(attrs={"type":"hidden"})

		return form

	def form_valid(self, form, **kwargs):
		form.instance.borrower = self.request.user
		form.instance.status = "o"

		return super().form_valid(form)


@login_required
def return_book(request, pk):
	book_instance = get_object_or_404(models.BookInstance, pk=pk)
	if book_instance.is_overdue:
		messages.error(request, "Return Failed due to overdue loan period. Please pay fine of Rs. 150/- and handover the book in person.")
	else:
		book_instance.due_back = None
		book_instance.status = "m"
		book_instance.borrower = None
		book_instance.save()
		messages.success(request, f"Thank you, for returning book ({book_instance.book.title}) on time.")
	return HttpResponseRedirect(reverse('my-borrowed'))