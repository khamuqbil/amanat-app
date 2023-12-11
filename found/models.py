from django.db import models
from datetime import date, datetime
from django.forms import CharField
from django.utils import timezone
from django.contrib.auth.models import User
import random
import qrcode
import os
from django.template.loader import render_to_string
from django.utils.formats import date_format
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import io
import urllib.parse
class Airport(models.Model):
	airport_code = models.CharField(max_length=5)
	airport_name = models.CharField(max_length=100)
	airport_email = models.EmailField(blank=True)

	def __str__(self):
		return self.airport_code

class Found(models.Model):
	LOCATIONS = (
		('DDT', 'Departer Domestic Terminal'),
		('DIT', 'Departer International Terminal'),
		('SEQ', 'Security Checkpoint'),
		('ADT', 'Arrival Domestic Terminal'),
		('AIT', 'Arrival International Terminal'),
		('CHT', 'Checkin Terminal'),
		('FPK', 'Front Parking'),
		('BPK', 'Back Parking'),
		('air', 'Air Side'),
	)

	airport = models.ForeignKey(Airport,default='AJF', on_delete=models.CASCADE)
	item = models.CharField(max_length=100, blank=False)
	date = models.DateField(null=False, default=date.today)
	valuable = models.BooleanField(default=False)
	locations = models.CharField(max_length=3, choices=LOCATIONS, default='DDT')
	model = models.CharField(max_length=100, null=True, help_text='BRAND, MODEL, MAKE')
	color = models.CharField(max_length=100, null=True)
	descriptions = models.TextField(blank=True, null=True)
	reported_by = models.CharField(max_length=200, blank=True, null=True)
	phone_number = models.CharField(max_length=10, blank=True, help_text='Enter phone number')
	created = models.DateTimeField(auto_now_add=True)
	update = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	image = models.ImageField(upload_to='found/%Y/%m/%d', blank=True)
	serial_number = models.CharField(max_length=4, unique=True, editable=False)
	is_delivered = models.BooleanField(default=False)
	qr_code = models.ImageField(upload_to='qrcodes/%Y/%m/%d', blank=True)

	def __str__(self):
		return self.item

	def save(self, *args, **kwargs):
		# Generate and assign a unique 4-digit serial number
		if not self.serial_number:
			self.serial_number = self.generate_serial_number()

		# Generate and save the QR code image
		if not self.qr_code:
			self.qr_code = self.generate_qr_code()

		super().save(*args, **kwargs)

	@staticmethod
	def generate_serial_number():
		# Generate a 4-digit random integer
		return str(random.randint(1000, 9999))
	def generate_qr_code(self):
		# Generate the content for the QR code
		content = f"Item: {self.item}\nDate: {date_format(self.date, format='SHORT_DATE_FORMAT')}\nSerial Number: {self.serial_number}"

		# Generate the QR code image
		qr = qrcode.QRCode(version=1, box_size=10, border=4)
		qr.add_data(content)
		qr.make(fit=True)
		qr_img = qr.make_image(fill_color="black", back_color="white")

		# Create an in-memory buffer to hold the image data
		image_buffer = io.BytesIO()
		qr_img.save(image_buffer, format='PNG')
		image_buffer.seek(0)

		# Create the S3 client
		s3 = boto3.client(
			's3',
			aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
			aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
			region_name=settings.AWS_S3_REGION_NAME
		)

		# Generate the QR code key
		qr_code_key = f"qrcodes/{self.date.strftime('%Y/%m/%d')}/{self.serial_number}.png"

		# Upload the QR code image to S3
		try:
			s3.upload_fileobj(image_buffer, settings.AWS_STORAGE_BUCKET_NAME, qr_code_key)
		except NoCredentialsError:
			# Handle the exception if AWS credentials are not provided
			return None

		# Generate a clickable URL for the uploaded image
		s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{qr_code_key}"

		return s3_url
	# def generate_qr_code(self):
	# 	# Generate the content for the QR code
	# 	content = f"Item: {self.item}\nDate: {date_format(self.date, format='SHORT_DATE_FORMAT')}\nSerial Number: {self.serial_number}"

	# 	# Generate the QR code image
	# 	qr = qrcode.QRCode(version=1, box_size=10, border=4)
	# 	qr.add_data(content)
	# 	qr.make(fit=True)
	# 	qr_img = qr.make_image(fill_color="black", back_color="white")

	# 	# Create the directories if they don't exist
	# 	qr_code_dir = f"qrcodes/{timezone.now().strftime('%Y/%m/%d')}"
	# 	os.makedirs(qr_code_dir, exist_ok=True)

		# Save the QR code image
		# qr_code_path = f"{qr_code_dir}/{self.item}_{self.serial_number}.png"
		# qr_img.save(qr_code_path)

		# return qr_code_path


class FoundSubmissionForm(models.Model):
	found = models.ForeignKey(Found, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	id_number = models.CharField(max_length=10)
	phone_number = models.CharField(max_length=10)
	created = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)



	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)

		self.found.is_delivered = True
		self.found.save()

	def __str__(self):
		return self.name


class Report(models.Model):
	report_name = models.CharField(max_length=100)
	descriptions = models.TextField()
	def __str__(self):
		return self.report_name

class SecurityForms(models.Model):
	FORM =(
		('LFI', 'محضر تسليم مضبوطات أو مفقودات'),
	)
	form = models.CharField(max_length=3, choices=FORM, default='LFI')
	date = models.DateField(null=False, default=date.today)
	created = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	image = models.ImageField(upload_to='found/%Y/%m/%d', blank=True)



class Clearance(models.Model):
	FORM =(
		('DEP', 'نقل سجناء'),
		('MED-EVAC', 'إخلاء طبي'),
		('FUNERAL', 'سيارة نقل الجنائز'),
		('OTHER', 'أخرى'),

	)
	form = models.CharField(max_length=8, choices=FORM, default='DDT')
	date = models.DateField(null=False, default=date.today)
	created = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
	image = models.ImageField(upload_to='found/%Y/%m/%d', blank=True)



class Security(models.Model):
	LOCATIONS = (
		('DDT', 'المغادرة'),
		('DIT', 'القدوم'),
		('SEQ', 'ضبط'),
		('ADT', 'تخلف'),
	)

	report_name = models.ForeignKey(Report, on_delete=models.CASCADE)
	locations = models.CharField(max_length=3, choices=LOCATIONS, default='DDT')
	item1 = models.CharField(max_length=100, blank=True)
	item2 = models.CharField(max_length=100, blank=True)
	item3 = models.CharField(max_length=100, blank=True)
	item4 = models.CharField(max_length=100, blank=True)
	item5 = models.CharField(max_length=100, blank=True)
	item6 = models.CharField(max_length=100, blank=True)
	item7 = models.CharField(max_length=100, blank=True)
	item8 = models.CharField(max_length=100, blank=True)
	item9 = models.CharField(max_length=100, blank=True)
	item10 = models.CharField(max_length=100, blank=True)
	item11 = models.CharField(max_length=100, blank=True)
	item12 = models.CharField(max_length=100, blank=True)
	item13 = models.CharField(max_length=100, blank=True)
	item14 = models.CharField(max_length=100, blank=True)
	item15 = models.CharField(max_length=100, blank=True)
	item16 = models.CharField(max_length=100, blank=True)
	item17 = models.CharField(max_length=100, blank=True)
	item18 = models.CharField(max_length=100, blank=True)
	item19 = models.CharField(max_length=100, blank=True)
	item20 = models.CharField(max_length=100, blank=True)
	deliverer = models.CharField(max_length=100)
	recipient = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	is_approved = models.BooleanField(default=False)

	def __str__(self):
		return self.report_name


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    associated_airport = models.ManyToManyField(Airport, null=True, blank=True)

    def __str__(self):
        return self.user.username