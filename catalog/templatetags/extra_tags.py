from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name="genre_merge")
def gerne_merge(genres):
	collection = []
	for genre in genres:
		link = f'<a href="{genre.get_absolute_url()}">{genre}</a>'
		collection.append(mark_safe(link))
	return collection\
