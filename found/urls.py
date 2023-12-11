from found.views import label_view
from . import views
from django.urls import path


urlpatterns = [
    path('', views.login_view, name='login'),
    path('index/', views.index, name='index'),
    # path('tables/', views.tables, name='tables'),
    path('found_detail/<found_id>/', views.found_detail, name='found-detail'),
    path('forms/', views.forms, name='forms'),
    path('register', views.register_user, name='register'),
    path('label/<int:pk>/', label_view, name='label-view'),
    path('tables/', views.tables, name='tables'),
    path('item_form/', views.add_item, name= 'item-form'),
    path('security-forms/', views.security_form, name= 'security-forms'),
    path('clearance-form/', views.clearance, name= 'clearance-form'),
    path('submission/', views.submissionform, name='submission-form'),
    path('security/', views.security, name='security-form'),
    path('deliver/<found_id>/', views.deliver, name='deliver-form'),
    path('submission_item/', views.submission, name='submission-item'),
    path('clearance_item/', views.clearance_table, name='clearance-item'),
    path('security_item/', views.security_table, name='security-item'),
    path('submissions_count/', views.submissions_count, name='submissions_count'),
    path('found-data/', views.found_data, name='found-data'),
    path('monthly-found-data/', views.monthly_found_data, name='monthly-found-data'),
    path('search-items/', views.search_items, name='search_items'),
    path('found-items/', views.display_found_items, name='display_found_items'),
    path('view_found_items/', views.view_found_items, name='view_found_items'),


]

