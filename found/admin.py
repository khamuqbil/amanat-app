from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import render_to_string
from .utils import generate_qr_code
from .models import *
from django.template.loader import get_template
from django.template import Context
from django.template import engines
from django.shortcuts import render
from django.template import engines
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.conf import settings
import io
import urllib.parse


admin.site.site_header = 'AJF Airport Lost and Found Item'
admin.site.site_title = 'AFJ Admin Area'
admin.site.index_title = 'AJF Admin'
admin.site.register(Security)
admin.site.register(Report)
admin.site.register(Clearance)
admin.site.register(SecurityForms)
# admin.site.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    filter_horizontal = ('associated_airport',)

admin.site.register(UserProfile, UserProfileAdmin)

def print_label(modeladmin, request, queryset):
	for obj in queryset:
		label_url = reverse('label-view', args=[obj.pk])
		label_link = f'<a href="{label_url}" target="_blank">Print Label</a>'
		print(f'Label for {obj.item}: {mark_safe(label_link)}')

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
	list_display = ['airport_code', 'airport_name', 'airport_email']



@admin.register(FoundSubmissionForm)
class FoundSubmissionFormAdmin(admin.ModelAdmin):
	list_display = ['found', 'name', 'id_number', 'phone_number']		



@admin.register(Found)
class FoundAdmin(admin.ModelAdmin):
	list_display = [ 'serial_number','item', 'date', 'valuable', 'locations', 'model', 'color','descriptions', 'image', 'qr_code_display', 'is_delivered']
	list_filter = ['date', 'locations', 'valuable', 'is_delivered']
	search_fields = ['item', 'date', 'locations', 'model', 'color','descriptions', 'serial_number']
	actions = [print_label]



	def qr_code_display(self, obj):
		# Generate the URL to view the QR code
		encoded_item_name = urllib.parse.quote(obj.item)
		qr_code_key = f"qrcodes/{obj.date.strftime('%Y/%m/%d')}/{obj.serial_number}.png"
		s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{qr_code_key}"
		
		return format_html('<a href="{}" target="_blank">View QR Code</a>', s3_url)

	qr_code_display.short_description = 'QR Code'

	# def image_display(self, obj):
	# 	# Generate the HTML code to display the image
	# 	image_html = f'<img src="{obj.image.url}" width="100" height="100">'
	# 	return format_html(image_html)

	# image_display.short_description = 'Image'

	def display_print_label(self, obj):
		label_url = reverse('label-view', args=[obj.pk])
		label_link = f'<a href="{label_url}" target="_blank">Print Label</a>'
		return mark_safe(label_link)

	display_print_label.short_description = 'Print Label'
	

	# In this example, the `print_label` function generates an HTML link (`Print Label`) that opens the 
	# label in a new tab when clicked. The `label-view` URL is 
	# assumed to be defined in your project's URL configuration.
	

	# def print_label(self, request, queryset):
	# 	# Generate the QR code and retrieve the label HTML
	# 	labels = []
	# 	django_engine = engines['django']
	# 	for obj in queryset:
	# 		# Retrieve the necessary fields from the model object
	# 		serial_number = obj.serial_number
	# 		item = obj.item

	# 		# Generate the QR code using the values from the model
	# 		qr_code_image = generate_qr_code(serial_number, item)

	# 		# Prepare the context for rendering the template
	# 		context = {'found_item': obj, 'qr_code_image': qr_code_image}

	# 		# Render the label template with the QR code image and other relevant data
	# 		label_html = django_engine.from_string(open('templates/label_template.html').read()).render(context)

	# 		# Append the label HTML to the list of labels
	# 		labels.append(label_html)

	# 	# Serve the label HTML as a downloadable file
	# 	combined_labels = ''.join(labels)
	# 	response = HttpResponse(combined_labels, content_type='text/html')
	# 	response['Content-Disposition'] = 'attachment; filename="found_items_label.html"'
	# 	return response


	# print_label.short_description = 'Print Label'
#     def print_label(self, request, queryset):
#         # Generate the QR code and retrieve the label HTML
#         label_html = ''
#         for obj in queryset:
#             # Retrieve the necessary fields from the model object
#             serial_number = obj.serial_number
#             item = obj.item

#             # Generate the QR code using the values from the model
#             qr_code_image = generate_qr_code(serial_number, item)

#             # Render the label template with the QR code image and other relevant data
#             label_html += render_to_string('label_template.html', {'found_item': obj, 'qr_code_image': qr_code_image})

#         # Serve the label HTML as a downloadable file
#         response = HttpResponse(label_html, content_type='text/html')
#         response['Content-Disposition'] = 'attachment; filename="found_items_label.html"'
#         return response


#     print_label.short_description = 'Print Label'
# @admin.register(found)
# class FoundAdmin(admin.ModelAdmin):
#     list_display = ['item', 'date', 'locations', 'created']
#     actions = ['print_label']

#     def print_label(self, request, queryset):
#         # Generate the QR code and retrieve the label HTML
#         label_html = ''
#         for obj in queryset:
#             # Retrieve the necessary fields from the model object
#             serial_number = obj.serial_number
#             item = obj.item

#             # Generate the QR code using the values from the model
#             qr_code_image = generate_qr_code(serial_number, item)

#             # Render the label template with the QR code image and other relevant data
#             label_html += render_to_string('label_template.html', {'found_item': obj, 'qr_code_image': qr_code_image})

#             # Serve the label HTML as a downloadable file
#             response = HttpResponse(label_html, content_type='text/html')
#             response['Content-Disposition'] = 'attachment; filename="found_items_label.html"'
#         return response


#     print_label.short_description = 'Print Label'
	# def print_label(self, request, queryset):
	#     label_html = render_to_string('label_template.html', {'found_items': queryset})
	#     response = HttpResponse(label_html, content_type='text/html')
	#     response['Content-Disposition'] = 'attachment; filename="found_items_label.html"'
	#     return response

	# print_label.short_description = 'Print Label'
	# 