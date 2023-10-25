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
from .models import Storage, StorageType, Sample
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
    storage_types = StorageType.objects.all()

    # Aplicar filtros basados en los parámetros GET
    name_filter = request.GET.get('name')
    type_filter = request.GET.get('type')
    status_filter = request.GET.get('status')

    if name_filter:
        storages = storages.filter(storage_name__icontains=name_filter)

    if type_filter:
        storages = storages.filter(STORAGE_TYPE_id_storagetype=type_filter)

    if status_filter:
        if status_filter == 'enabled':
            storages = storages.filter(storage_state=True)
        elif status_filter == 'disabled':
            storages = storages.filter(storage_state=False)

    return render(request, 'space_list.html', {'spaces': storages, 'storage_types': storage_types})


@csrf_exempt
@require_POST
def update_space_status(request):
    try:
        data = json.loads(request.body)
        if not all(isinstance(space_id, str) and isinstance(status, bool) for space_id, status in data['changes'].items()):
            return JsonResponse({'error': 'Formato de datos inválido'}, status=400)

        for space_id, status in data['changes'].items():
            storage = Storage.objects.get(pk=space_id)
            storage.storage_state = status
            storage.save()

        return JsonResponse({'message': 'Estados actualizados con éxito'})

    except Storage.DoesNotExist:
        return JsonResponse({'error': 'Espacio no encontrado'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except ValueError as ve:
        return JsonResponse({'error': f'Error de valor: {str(ve)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)


@csrf_exempt
@require_POST
def delete_spaces(request):
    try:
        data = json.loads(request.body)
        print("Received data:", data)
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
    if request.method == "POST":
        # Extraer datos del formulario
        subject_id = request.POST.get('subject_id')
        sample_date = request.POST.get('sample_date')
        preservation_state = True if request.POST.get(
            'preservation_state') == 'frozen' else False
        volume = float(request.POST.get('volume'))  # Convertir a float
        specification = request.POST.get('specification')
        freezer_number = request.POST.get('freezer_number')
        rack_number = request.POST.get('rack_number')
        box_number = request.POST.get('box_number')
        # Aquí puedes agregar lógica para manejar los números de freezer, rack y caja si es necesario

        # Crear una instancia del modelo Sample y guardarla
        sample = Sample(
            id_subject=subject_id,
            date_sample=sample_date,
            state_preservation=preservation_state,
            ml_volume=volume,
            state_analysis=False,  # Valor predeterminado: No analizada
            specification=specification,
            # SHIPMENT_id_shipment se dejará en blanco por ahora
        )
        sample.save()

        # Redirigir según el botón que se presionó
        action = request.POST.get('action')
        if action == 'add_another':
            messages.success(
                request, '¡Éxito! Muestra registrada correctamente. Puedes agregar otra muestra.')
            return redirect('create_sample')
        else:
            messages.success(
                request, '¡Éxito! Muestra registrada correctamente.')
            return redirect('home')

    # Query available freezers, racks, and boxes
    freezers = Storage.objects.filter(
        STORAGE_TYPE_id_storagetype__name_storagetype=3)
    racks = Storage.objects.filter(
        STORAGE_TYPE_id_storagetype__name_storagetype=2)
    boxes = Storage.objects.filter(
        STORAGE_TYPE_id_storagetype__name_storagetype=1)

    context = {
        'freezers': freezers,
        'racks': racks,
        'boxes': boxes,
    }

    return render(request, 'create_sample.html', context)


def sample_list(request):
    samples = Sample.objects.all()

    # Si el método es GET y hay datos en el formulario
    if request.method == "GET":
        subject_id = request.GET.get('subject_id')
        sample_date = request.GET.get('sample_date')
        freezer_number = request.GET.get('freezer_number')
        rack_number = request.GET.get('rack_number')
        box_number = request.GET.get('box_number')

        if subject_id:
            samples = samples.filter(id_subject=subject_id)
        if sample_date:
            samples = samples.filter(date_sample=sample_date)
        #  para el freezer_number, rack_number, y box_number
        if freezer_number:

            samples = samples.filter(freezer_number=freezer_number)
        if rack_number:

            samples = samples.filter(rack_number=rack_number)
        if box_number:

            samples = samples.filter(box_number=box_number)

    context = {
        'samples': samples
    }

    return render(request, 'sample_list.html', context)


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


def shipments_report(request):
    return render(request, 'shipments_report.html')


def samples_report(request):
    return render(request, 'samples_report.html')
