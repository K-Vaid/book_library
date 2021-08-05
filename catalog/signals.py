from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import UserToken

@receiver(post_save, sender=User)
def create_token(sender, instance, created, **kwargs):
	if created:
		profile = UserToken.objects.create(user=instance)
		profile.save()