from django.contrib import admin
from django.urls import path
from muestras import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('create_account/', views.create_accounts, name='create_account'),
    path('user_list/', views.user_list),
    path('create_space/', views.create_space),
    path('space_list/', views.space_list),
    path('', views.home),
    path('create_sample/', views.create_sample),
    path('sample_list/', views.sample_list),
    path('trazability/', views.trazability)

]
