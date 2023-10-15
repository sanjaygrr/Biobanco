from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import IntegrityError
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Storage, StorageType
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
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


def create_space(request):
    if request.method == 'POST':
        storage_type_id = request.POST.get('storage_type')
        storage_name = request.POST.get('storage_name')
        storage_state = request.POST.get('storage_state')
        storage_description = request.POST.get('storage_description')

        if not all([storage_type_id, storage_name, storage_state, storage_description]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('create_space')

        storage_exists = Storage.objects.filter(
            storage_name=storage_name,
            STORAGE_TYPE_id_storagetype=storage_type_id
        ).exists()

        if storage_exists:
            messages.error(request, 'Este espacio ya existe.')
        else:
            new_storage = Storage(
                storage_name=storage_name,
                storage_state=bool(int(storage_state)),
                storage_description=storage_description,
                STORAGE_TYPE_id_storagetype_id=storage_type_id
            )
            new_storage.save()

            messages.success(request, 'Espacio registrado con éxito!')
            return redirect('create_space')

    storage_types = StorageType.objects.all()
    return render(request, 'create_space.html', {'storage_types': storage_types})


def space_list(request):
    storages = Storage.objects.select_related(
        'STORAGE_TYPE_id_storagetype').all()
    return render(request, 'space_list.html', {'spaces': storages})


@csrf_exempt
@require_POST
def update_space_status(request):
    try:
        data = json.loads(request.body)
        if not all(isinstance(space_id, str) and isinstance(status, bool) for space_id, status in data.items()):
            return JsonResponse({'error': 'Formato de datos inválido'}, status=400)

        for space_id, status in data.items():
            storage = Storage.objects.get(pk=space_id)
            storage.storage_state = status
            storage.save()

        return JsonResponse({'message': 'Estado actualizado con éxito'})
    except Storage.DoesNotExist:
        return JsonResponse({'error': 'Espacio no encontrado'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def delete_spaces(request):
    try:
        data = json.loads(request.body)
        if not all(isinstance(space_id, str) and isinstance(should_delete, bool) for space_id, should_delete in data.items()):
            return JsonResponse({'error': 'Formato de datos inválido'}, status=400)

        for space_id, should_delete in data.items():
            if should_delete:
                storage = Storage.objects.get(pk=space_id)
                storage.delete()

        return JsonResponse({'message': 'Espacios eliminados con éxito'})
    except Storage.DoesNotExist:
        return JsonResponse({'error': 'Espacio no encontrado'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def create_sample(request):
    return render(request, 'create_sample.html')


def sample_list(request):
    return render(request, 'sample_list.html')


def trazability(request):
    return render(request, 'trazability.html')


def shipments(request):
    return render(request, 'shipments.html')


def login(request):
    return render(request, 'login.html')


def create_password(request):
    return render(request, 'create_password.html')


def shipments_select(request):
    return render(request, 'shipments_select.html')
