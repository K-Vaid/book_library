from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import models



# Register your models here.
admin.site.unregister(User)
admin.site.register(models.Genre)
admin.site.register(models.Language)


class UserTokenAdmin(admin.StackedInline):
	model = models.UserToken
	can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
	inlines = [UserTokenAdmin]


class BookInline(admin.StackedInline):
	model = models.Book
	extra = 0
	classes = ['collapse',]


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
	inlines = [BookInline]
	list_display = ('first_name', 'last_name', 'date_of_birth', 'date_of_death')
	search_fields = ('first_name', 'last_name')
	fields = ('first_name', 'last_name', ('date_of_birth', 'date_of_death'))


@admin.register(models.BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
	list_display = ('book', 'id', 'status', 'borrower', 'due_back')
	list_filter = ('status', 'due_back')
	search_fields = ('book',)
	fieldsets = (
		(None, {
			'fields' : ('id', 'book', 'imprint')
		}),
		('Availability', {
			'fields' : ('status', ('borrower', 'due_back'))
		})
	)


class BookInstanceInline(admin.TabularInline):
	model = models.BookInstance
	extra = 0
	# classes = ['collapse',]


@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
	inlines = [BookInstanceInline]
	list_display = ('title', 'author', 'display_genre', 'display_language')
	list_filter = ('genre', 'language')
	search_fields = ('title', 'genre', 'author')
	fieldsets = (
		(None, {
			'fields' : ('title', 'summary', ('author', 'isbn'))	
		}),
		('Additional Information', {
			'fields' : ('genre', 'language'),
			'classes' : ('collapse',)
		}),
	)