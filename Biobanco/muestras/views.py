from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import IntegrityError
from django.http import HttpResponse
from .models import Space
from django.contrib import messages


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


def create_space(request):
    # Check if the request is of type POST
    if request.method == 'POST':
        # Get form data
        space_type = request.POST.get('type')
        name = request.POST.get('name')
        description = request.POST.get('description')
        status = request.POST.get('status')

        # Validate data (optional but recommended)
        if not all([space_type, name, description, status]):
            # You can send an error message to the user if any field is empty
            return render(request, 'create_space.html', {'error': 'All fields are required'})

        # Create and save the new space in the database
        new_space = Space(type=space_type, name=name,
                          description=description, status=status)
        new_space.save()

        # Query the space we just saved
        # Note: This is an example and may not be necessary in your case,
        # as `new_space` already contains the object we just saved.
        saved_space = Space.objects.get(id=new_space.id)

        # Now you can use `saved_space` to do something, e.g.,
        # pass it to a template or use its attributes in some additional logic.

        messages.success(request, 'Space registered successfully!')

        return redirect('/create_space')

    # If the request is not POST, simply render the page as is
    return render(request, 'create_space.html')


def space_list(request):
    spaces = Space.objects.all()  # Obtén todos los espacios de la base de datos
    return render(request, 'space_list.html', {'spaces': spaces})


def create_sample(request):
    return render(request, 'create_sample.html')


def sample_list(request):
    return render(request, 'sample_list.html')


def trazability(request):
    return render(request, 'trazability.html')
