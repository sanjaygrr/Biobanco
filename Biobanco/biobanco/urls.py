from django.contrib import admin
from django.urls import path
from muestras import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('user_list/', views.user_list),
    path('create_space/', views.create_space, name='create_space'),
    path('space_list/', views.space_list, name='space_list'),
    path('', views.login_screen),
    path('create_sample/', views.create_sample, name='create_sample'),
    path('sample_list/', views.sample_list, name='sample_list'),
    path('trazability/', views.trazability),
    path('update_space_status/',
         views.update_space_status, name='update_space_status'),
    path('shipments/', views.shipments, name='shipments'),
    path('login_screen/', views.login_screen),
    path('create_password/', views.create_password),
    path('shipments_select/', views.shipments_select, name='shipments_select'),
    path('update-shipment/', views.update_samples_shipment,
         name='update_samples_shipment'),
    path('delete_spaces/', views.delete_spaces, name='delete_spaces'),
    path('delete_sample/<sample_id>/', views.delete_sample, name='delete_sample'),
    path('shipments_report/', views.shipments_report),
    path('samples_report/', views.samples_report),
    path('edit_sample/<sample_id>/', views.edit_sample, name='edit_sample'),
]
