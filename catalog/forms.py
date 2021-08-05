import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class DateInput(forms.DateInput):
    input_type = 'date'

class RenewBookForm(forms.Form):
	renewal_date = forms.DateField( widget = DateInput(),
									help_text = "Enter a renewal date between now and 4 weeks (default 3 weeks).")

	def clean_renewal_date(self):
		date = self.cleaned_data['renewal_date']

		if date < datetime.date.today():
			raise ValidationError(_("Invalid date - Renewal in past."))

		if date > datetime.date.today() + datetime.timedelta(weeks=4):
			raise ValidationError(_("Invalid date - Renewal more than 4 weeks ahead."))

		return date


class SignupForm(UserCreationForm):
	class Meta:
		model = User
		fields = ["username", "email", "password1", "password2"]

class ProfileForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ["username", "email", "first_name", "last_name"]


class CustomAuthForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        
        if not user.is_active:
            raise ValidationError(
                _("Please verify your Email ID before Login."),
                code="inactive",
            )
