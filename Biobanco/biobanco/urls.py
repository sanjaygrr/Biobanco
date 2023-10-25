from django.contrib import admin
from django.urls import path
from muestras import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('create_account/', views.create_accounts, name='create_account'),
    path('user_list/', views.user_list),
    path('create_space/', views.create_space, name='create_space'),
    path('space_list/', views.space_list, name='space_list'),
    path('', views.login),
    path('create_sample/', views.create_sample, name='create_sample'),
    path('sample_list/', views.sample_list),
    path('trazability/', views.trazability),
    path('update_space_status/',
         views.update_space_status, name='update_space_status'),
    path('shipments/', views.shipments, name='shipments'),
    path('login/', views.login),
    path('create_password/', views.create_password),
    path('shipments_select/', views.shipments_select),
    path('delete_spaces/', views.delete_spaces, name='delete_spaces'),
    path('shipments_report/', views.shipments_report),
    path('samples_report/', views.samples_report),
]
