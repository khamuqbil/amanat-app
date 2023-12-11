from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm, ItemSearchForm, TimePeriodForm
from .forms import FoundForm, SubmissionForm, SecurityForm
from .forms import FormSecurity, ClearanceForm, FoundSearchForm
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth
from django.http import JsonResponse
from datetime import timedelta


def page_403(request, exception):

	return render(request, 'home/page-403.html', status=403)


def page_404(request, exception):

	return render(request, 'home/page-404.html', status=404)

def page_500(request):

	return render(request, 'home/page-500.html', status=500)

def login_view(request):
	form = LoginForm(request.POST or None)

	msg = None

	if request.method == "POST":

		if form.is_valid():
			username = form.cleaned_data.get("username")
			password = form.cleaned_data.get("password")
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect("/index")
			else:
				msg = 'Invalid credentials'
		else:
			msg = 'Error validating the form'

	return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
	msg = None
	success = False

	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get("username")
			raw_password = form.cleaned_data.get("password1")
			user = authenticate(username=username, password=raw_password)

			msg = 'User Created Successfully...'
			success = True

			return redirect("/")

		else:
			msg = 'Form is not valid'
	else:
		form = SignUpForm()

	return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})



def label_view(request, pk):
	found_instance = get_object_or_404(Found, pk=pk)
	return render(request, 'label_template.html', {'found': found_instance})



def forms(request):


	return render(request, 'home/forms.html')

@login_required(login_url='/')
def index(request):
	airport = Airport.objects.all()
	found = Found.objects.all().count()
	foundf = Found.objects.filter(is_delivered=False).count()
	foundt = Found.objects.filter(is_delivered=True).count()
	users_with_submissions = User.objects.annotate(submission_count=Count('found'))
	context ={
	'airport': airport,
	'found': found,
	'foundf': foundf,
	'foundt': foundt,
	'users_with_submissions': users_with_submissions,
	}
	return render(request, 'home/index.html', context)

@login_required(login_url='/')
def tables(request):
	foundf = Found.objects.filter(is_delivered=False).order_by('-date')
	foundt = Found.objects.filter(is_delivered=True).order_by('-date')
	sub = FoundSubmissionForm.objects.all()
	form = FoundSearchForm()
	search_query = None

	if request.method == 'GET':
		form = FoundSearchForm(request.GET)
		if form.is_valid():
			search_query = form.cleaned_data['search_query']
			foundf = Found.objects.filter(item__icontains=search_query)

	for foundsf in foundf:
		foundsf.qr_code_url = f"{foundsf.generate_qr_code()}"

	for foundst in foundt:
		foundst.qr_code_url = f"{foundst.generate_qr_code()}"

	p = Paginator(foundf, 5)
	page = request.GET.get('page')
	found_list = p.get_page(page)
	nums = 'a' * found_list.paginator.num_pages

	pt = Paginator(foundt, 5)
	paget = request.GET.get('paget')  # Use a different variable for paginating foundt
	found_listt = pt.get_page(paget)  # Use paget here
	numst = 'a' * found_listt.paginator.num_pages

	context = {
		'foundf': foundf,
		'foundt': foundt,
		'nums': nums,
		'found_list': found_list,
		'found_listt': found_listt,
		'numst': numst,
		'sub': sub,
		'form': form,
		'search_query': search_query,
	}

	return render(request, 'home/tables.html', context)

@login_required
def found_detail(request, found_id):
	found = get_object_or_404(Found, pk=found_id)

	context = {
	'found': found,
	}
	return render(request, 'home/found_detail.html', context)

@login_required
def submission(request):
	sub = FoundSubmissionForm.objects.all().order_by('-created')

	p = Paginator(sub, 5)
	page = request.GET.get('page')
	sub_list = p.get_page(page)
	nums = 'a' * sub_list.paginator.num_pages

	context ={
	'sub': sub,
	'sub_list': sub_list,
	'nums': nums,
	}

	return render(request, 'home/submission-item.html', context)


@login_required
def clearance_table(request):
	sub = Clearance.objects.all().order_by('-date')


	p = Paginator(sub, 5)
	page = request.GET.get('page')
	sub_list = p.get_page(page)
	nums = 'a' * sub_list.paginator.num_pages

	context ={
	'sub': sub,
	'sub_list': sub_list,
	'nums': nums,
	}

	return render(request, 'home/clearance.html',context)


@login_required
def security_table(request):
	sub = SecurityForms.objects.all().order_by('-date')


	p = Paginator(sub, 5)
	page = request.GET.get('page')
	sub_list = p.get_page(page)
	nums = 'a' * sub_list.paginator.num_pages

	context ={
	'sub': sub,
	'sub_list': sub_list,
	'nums': nums,
	}

	return render(request, 'home/security.html',context)

@login_required(login_url='/')
def add_item(request):

	if request.method == 'POST':
		form = FoundForm(request.POST,request.FILES, user=request.user)
		if form.is_valid():
			form.save()
			messages.success(request,'Item add Successfuly...')
			return redirect('/table')
	else:
		form = FoundForm(user=request.user)

	return render(request, 'home/item_form.html',{'form': form})

@login_required(login_url='/')
def submissionform(request):
	form = SubmissionForm()  # Move the form instantiation outside the if condition

	if request.method == 'POST':
		form = SubmissionForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Item Delivered Successfully...')
			return redirect('/table')

	return render(request, 'home/submission.html', {'form': form})
@login_required(login_url='/')
def deliver(request, found_id):

	# found = get_object_or_404(Found, pk=found_id, is_delivered=False)

	# # submission = FoundSubmissionForm.objects.filter(found_id=(found))
	# if request.method == 'POST':
	#     form = SubmissionForm(request.POST or None, instance=found)
	#     if form.is_valid():
	#         form.save()
	#         messages.success(request, 'Item Delivered Successfuly...')
	#         return redirect('/table')
	# else:
	#     form = SubmissionForm()

	# return render(request, 'home/deliver.html', {'form': form})
	found = get_object_or_404(Found, pk=found_id, is_delivered=False)

	if request.method == 'POST':
		form = SubmissionForm(request.POST or None, instance=found)
		if form.is_valid():
			form.save()
			messages.success(request, 'Item Delivered Successfully...')
			return redirect('/table')
	else:
		form = SubmissionForm(initial={'found': found})

	return render(request, 'home/deliver.html', {'form': form})

@login_required(login_url='/')
def security(request):
	if request.method == 'POST':
		form = SecurityForm(request.POST,request.FILES)
		if form.is_valid():
			form.save()
			messages.success(request,'Items add Successfuly...')
			return redirect('/table')
	else:
		form = SecurityForm()


	return render(request, 'home/security-form.html', {'form': form})

@login_required(login_url='/')
def approve_item(request, item_id):
	item = get_object_or_404(Security, pk=item_id)

	# Check if the user is authorized to approve the item
	if not request.user.is_superuser:
		return render(request, 'error.html', {'message': 'Unauthorized access'})

	# Approve the item and assign the recipient
	item.is_approved = True
	item.recipient = request.user
	item.save()

	return render(request, 'success.html', {'message': 'Item approved successfully'})

@login_required
def pending_requests(request):
	# Retrieve all pending items
	pending_items = Security.objects.filter(is_approved=False)

	return render(request, 'pending_requests.html', {'pending_items': pending_items})


@login_required(login_url='/')
def clearance(request):

	if request.method == 'POST':
		form = ClearanceForm(request.POST,request.FILES, user=request.user)
		if form.is_valid():
			form.save()
			messages.success(request,'Form add Successfuly...')
			return redirect('/clearance_item')
	else:
		form = ClearanceForm(user=request.user)

	return render(request, 'home/clearance_form.html',{'form': form})


@login_required(login_url='/')
def security_form(request):

	if request.method == 'POST':
		form = FormSecurity(request.POST,request.FILES, user=request.user)
		if form.is_valid():
			form.save()
			messages.success(request,'Form add Successfuly...')
			return redirect('/security_item')
	else:
		form = FormSecurity(user=request.user)

	return render(request, 'home/security_upload_form.html',{'form': form})

@login_required(login_url='/')
def submissions_count(request):
	users_with_submissions = User.objects.annotate(submission_count=Count('found'))
	# users_with_upload = User.objects.annotate(submission_count=Count('form'))
	context = {
		'users_with_submissions': users_with_submissions,
	}
	return render(request, 'home/submissions_count.html', context)

@login_required(login_url='/')
def found_data(request):
	# Aggregate data by date
	data = Found.objects.annotate(date=TruncDay('date')).values('date').annotate(count=Count('id')).order_by('date')
	
	# Prepare data for the chart
	labels = [item['date'].strftime('%Y-%m-%d') for item in data]
	series = [[item['count'] for item in data]]

	return JsonResponse({'labels': labels, 'series': [series]})

@login_required(login_url='/')
def monthly_found_data(request):
	# Aggregate data by month
	data = Found.objects.annotate(month=TruncMonth('date')).values('month').annotate(count=Count('id')).order_by('month')
	
	# Prepare data for the chart
	labels = [item['month'].strftime('%Y-%m') for item in data]
	series = [[item['count'] for item in data]]

	return JsonResponse({'labels': labels, 'series': [series]})

def search_items(request):
	form = ItemSearchForm(request.GET or None)
	matches = None

	if form.is_valid():
		# Get form data
		query_data = form.cleaned_data
		# Filter the Found model based on form data
		matches = Found.objects.all()
		if query_data.get('item'):
			matches = matches.filter(item__icontains=query_data['item'])
		if query_data.get('model'):
			matches = matches.filter(model__icontains=query_data['model'])
		if query_data.get('color'):
			matches = matches.filter(color__icontains=query_data['color'])
		if query_data.get('date'):
			matches = matches.filter(date=query_data['date'])
		if query_data.get('descriptions'):
			matches = matches.filter(descriptions__icontains=query_data['descriptions'])
		# Add more filters as needed

	return render(request, 'home/search_items.html', {'form': form, 'matches': matches})

# def display_found_items(request):
#     # Fetch all found items with images
#     items_with_images = Found.objects.exclude(image='').order_by('-date')
#     return render(request, 'home/display_found_items.html', {'items': items_with_images})

def display_found_items(request):
	# Fetch all found items with images that are not delivered and not valuable
	items_with_images = Found.objects.filter(is_delivered=False, valuable=False).exclude(image='').order_by('-date')
	return render(request, 'home/display_found_items.html', {'items': items_with_images})


@login_required(login_url='/')
def view_found_items(request):
	form = TimePeriodForm(request.GET or None)
	items = None

	if form.is_valid():
		months = int(form.cleaned_data['time_period'])
		print("Selected months:", months)  # Debugging

		date_threshold = timezone.now() - timedelta(days=30 * months)
		print("Date threshold:", date_threshold)  # Debugging

		items = Found.objects.filter(
			is_delivered=False,
			date__lte=date_threshold
		).exclude(image='').order_by('date')

	return render(request, 'home/view_found_items.html', {'form': form, 'items': items})