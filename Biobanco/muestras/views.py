from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import IntegrityError

from django.http import HttpResponse


def home(request):
    return render(request, 'home.html')


def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm})

    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('home')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'Username already exists'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            "error": 'Password do not match'
        })


def create_accounts(request):
    return render(request, 'create_account.html')


def user_list(request):
    users = User.objects.all()  # Obtén todos los usuarios de la base de datos
    return render(request, 'user_list.html', {'users': users})


def create_slot(request):
    return render(request, 'create_slot.html')


def slot_list(request):
    return render(request, 'slot_list.html')


def create_sample(request):
    return render(request, 'create_sample.html')


def sample_list(request):
    return render(request, 'sample_list.html')


def trazability(request):
    return render(request, 'trazability.html')
