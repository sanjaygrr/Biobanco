from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import IntegrityError
from .models import Space
from django.contrib import messages


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


def create_space(request):
    # Verificar si la solicitud es de tipo POST
    if request.method == 'POST':
        # Obtener los datos del formulario
        space_type = request.POST.get('type')
        name = request.POST.get('name')
        description = request.POST.get('description')
        status = request.POST.get('status')

        # Validar los datos (opcional pero recomendado)
        if not all([space_type, name, description, status]):
            # Puedes enviar un mensaje de error al usuario si algún campo está vacío
            return render(request, 'create_space.html', {'error': 'Todos los campos son obligatorios'})

        # Crear y guardar el nuevo espacio en la base de datos
        new_space = Space(type=space_type, name=name,
                          description=description, status=status)
        new_space.save()

        # Consultar el espacio que acabamos de guardar
        # Nota: Esto es un ejemplo y puede no ser necesario en tu caso,
        # ya que `new_space` ya contiene el objeto que acabamos de guardar.
        saved_space = Space.objects.get(id=new_space.id)

        # Ahora puedes usar `saved_space` para hacer algo, por ejemplo,
        # pasarlo a un template o usar sus atributos en alguna lógica adicional.

        messages.success(request, '¡Espacio registrado exitosamente!')

        return redirect('create_space/')

    # Si la solicitud no es POST, simplemente renderizar la página como está
    return render(request, 'create_space.html')


def slot_list(request):
    return render(request, 'slot_list.html')


def create_sample(request):
    return render(request, 'create_sample.html')


def sample_list(request):
    return render(request, 'sample_list.html')


def trazability(request):
    return render(request, 'trazability.html')
