from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .widgets import DatePickerInput, TimePickerInput, DateTimePickerInput
from django.contrib.admin.widgets import AdminDateWidget, AdminSplitDateTime, AdminDateWidget
from django.forms import ModelForm
# from .models import MultiTextModel
from .models import *
import random
import qrcode
import io
import boto3
from django.conf import settings


class LoginForm(forms.Form):
	username = forms.CharField(
		widget=forms.TextInput(
			attrs={
				"placeholder": "Username",
				"class": "form-control"
			}
		))
	password = forms.CharField(
		widget=forms.PasswordInput(
			attrs={
				"placeholder": "Password",
				"class": "form-control"
			}
		))


class SignUpForm(UserCreationForm):
	username = forms.CharField(
		widget=forms.TextInput(
			attrs={
				"placeholder": "Username",
				"class": "form-control"
			}
		))
	email = forms.EmailField(
		widget=forms.EmailInput(
			attrs={
				"placeholder": "Email",
				"class": "form-control"
			}
		))
	password1 = forms.CharField(
		widget=forms.PasswordInput(
			attrs={
				"placeholder": "Password",
				"class": "form-control"
			}
		))
	password2 = forms.CharField(
		widget=forms.PasswordInput(
			attrs={
				"placeholder": "Password check",
				"class": "form-control"
			}
		))

	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2')

class FoundSearchForm(forms.Form):
	search_query = forms.CharField(label='Search', max_length=100)

class FoundForm(ModelForm):
	image = forms.ImageField(required=False)
	class Meta:
		model = Found
		fields = ['airport', 'date', 'valuable', 'item', 'locations', 'model', 'color', 'descriptions', 'reported_by', 'phone_number', 'user','image']

		widgets = {

			'airport': forms.Select(attrs={'class': 'form-select w-100 mb-0 text-center'}),
			'date': DatePickerInput(attrs={'placeholder': 'DD/MM/YYYY', 'data-date-format':'DD/MM/YYYY', 'class': 'form-control text-center'}),
			'valuable': forms.CheckboxInput(attrs={'class' : 'form-check-input'}), 
			'item':forms.TextInput(attrs={'class' : 'form-control text-center', 'placeholder': 'Item Name',}),
			'locations': forms.Select(attrs={'class': 'form-select mb-0 text-center'}),
			'model' : forms.TextInput(attrs={'class': 'form-control text-center', 'placeholder': 'Gussi'}),
			'color': forms.TextInput(attrs={'class': 'form-control mb-0 text-center','placeholder': 'Black'}),
			'descriptions': forms.Textarea(attrs={'class': 'form-control text-center', 'placeholder': 'Descriptions or Notes...',}),
			'reported_by': forms.TextInput(attrs={'class': 'form-control text-center', 'placeholder': 'Khalid Almuqbil',}),
			'phone_number': forms.TextInput(attrs={'class': 'form-control text-center', 'placeholder': '0555391752',}),
			'user' : forms.HiddenInput(),
			'image': forms.ImageField(required=False),
		}
		labels = {
			'valuable': 'Valuable ',
			'locations': 'Locations  ',
		}

	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)
		if user:
			self.fields['user'].initial = user.id
			self.fields['user'].widget = forms.HiddenInput()


class SubmissionForm(ModelForm):
	class Meta:
		model = FoundSubmissionForm
		fields = ['found', 'name', 'id_number', 'phone_number', 'user']

		widgets = {

			'found': forms.Select(attrs={'class': 'form-select w-100 mb-0 text-center'}),
			'name': forms.TextInput(attrs={'class' : 'form-control text-center'}),
			'id_number':forms.TextInput(attrs={'class' : 'form-control text-center'}),
			'phone_number': forms.TextInput(attrs={'class': 'form-control text-center'}),
			'user' : forms.HiddenInput(),
		}
	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)
		if user:
			self.fields['user'].initial = user.id
			self.fields['user'].widget = forms.HiddenInput()


class SecurityForm(ModelForm):
	class Meta:
		model = Security
		fields = '__all__'
		# widgets = {
		#     'texts': forms.Textarea(attrs={'rows': 5, 'multiple': True})
		# }

class ClearanceForm(ModelForm):
	image = forms.ImageField(required=False)
	class Meta:
		model = Clearance
		fields = ['form', 'date', 'image', 'user']

		widgets = {

			'form': forms.Select(attrs={'class': 'form-select w-100 mb-0 text-center'}),
			'date': DatePickerInput(attrs={'placeholder': 'DD/MM/YYYY', 'data-date-format':'DD/MM/YYYY', 'class': 'form-control text-center'}),
			'image': forms.ImageField(required=False),
			'user' : forms.HiddenInput(),
		}
	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)
		if user:
			self.fields['user'].initial = user.id
			self.fields['user'].widget = forms.HiddenInput()


class FormSecurity(ModelForm):
	image = forms.ImageField(required=False)
	class Meta:
		model = SecurityForms
		fields = ['form', 'date', 'image', 'user']

		widgets = {

			'form': forms.Select(attrs={'class': 'form-select w-100 mb-0 text-center'}),
			'date': DatePickerInput(attrs={'placeholder': 'DD/MM/YYYY', 'data-date-format':'DD/MM/YYYY', 'class': 'form-control text-center'}),
			'image': forms.ImageField(required=False),
			'user' : forms.HiddenInput(),
		}
	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)
		if user:
			self.fields['user'].initial = user.id
			self.fields['user'].widget = forms.HiddenInput()

class ItemSearchForm(forms.Form):
	widgets = {

			'date': DatePickerInput(),
		}
	item = forms.CharField(max_length=100, required=False)
	model = forms.CharField(max_length=100, required=False)
	color = forms.CharField(max_length=100, required=False)
	date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
	descriptions = forms.CharField(widget=forms.Textarea, required=False)

class TimePeriodForm(forms.Form):
    TIME_PERIOD_CHOICES = (
        (1, 'More than 1 month'),
        (2, 'More than 2 months'),
        (3, 'More than 3 months'),
        (4, 'More than 4 months'),
        (5, 'More than 5 months'),
        (6, 'More than 6 months'),
        (12, 'More than 12 months'),
        # Add more options as needed
    )
    time_period = forms.ChoiceField(choices=TIME_PERIOD_CHOICES, label="Select Time Period")