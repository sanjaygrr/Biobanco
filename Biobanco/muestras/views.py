from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import IntegrityError
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.db.models import Q, Prefetch
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Storage, StorageType, Sample, Location
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


def is_valid_int(value):
    """Función de ayuda para comprobar si un valor puede ser convertido a int."""
    try:
        int(value)
        return True
    except ValueError:
        return False


def create_sample(request):
    if request.method == "POST":
        # Obtener y procesar datos del formulario
        id_subject = request.POST.get('id_subject')
        date_sample = request.POST.get('date_sample')
        ml_volume = float(request.POST.get('ml_volume'))
        state_analysis = request.POST.get('state_analysis') == "1"
        state_preservation = request.POST.get('state_preservation') == "1"
        specification = request.POST.get('specification')
        shipment_id = request.POST.get('SHIPMENT_id_shipment')

        # Crear una nueva instancia de muestra
        sample = Sample(
            id_subject=id_subject,
            date_sample=date_sample,
            ml_volume=ml_volume,
            state_analysis=state_analysis,
            state_preservation=state_preservation,
            specification=specification
        )

        if shipment_id:
            sample.SHIPMENT_id_shipment = int(shipment_id)

        sample.save()

        # Lógica de Guardado de Ubicaciones
        for storage_value_key in ['freezer_id', 'rack_id', 'caja_id']:
            storage_value = request.POST.get(storage_value_key)
            storage_type, storage_name = storage_value.split('-')

            # Buscar el objeto Storage usando el nombre del almacenamiento:
            storage_obj = Storage.objects.filter(
                storage_name=storage_name).first()
            if storage_obj:
                cell_value = int(request.POST.get('cell'))
                location = Location(
                    cell=cell_value,
                    SAMPLE_id_sample_1=sample,
                    STORAGE_id_storage_1=storage_obj,
                    STORAGE_TYPE_id_storagetype_id=int(storage_type)
                )
                location.save()
                print(
                    f"Ubicación para {storage_obj.storage_name} guardada con éxito.")
            else:
                print(
                    f"Objeto Storage no encontrado para id: {storage_value}.")

        # Redirigir según la acción
        action = request.POST.get('action')
        if action == "add_another":
            return redirect('create_sample')
        else:
            return redirect('home')

    else:
        # Cargar datos para el formulario
        storages = Storage.objects.all().order_by('storage_name')
        storage_types = StorageType.objects.all().order_by('name_storagetype')

        context = {
            'storages': storages,
            'storage_types': storage_types
        }

        return render(request, 'create_sample.html', context)


def sample_list(request):
    samples = Sample.objects.all().select_related('location_set')
    samples = Sample.objects.all().prefetch_related(
        Prefetch('location_set', queryset=Location.objects.select_related(
            'STORAGE_id_storage_1'))
    )

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

        # Filtros para freezer_number, rack_number, y box_number usando el modelo relacionado `Location` y luego `Storage`
        if freezer_number:
            samples = samples.filter(
                location__STORAGE_id_storage_1__freezer_number=freezer_number)
        if rack_number:
            samples = samples.filter(
                location__STORAGE_id_storage_1__rack_number=rack_number)
        if box_number:
            samples = samples.filter(
                location__STORAGE_id_storage_1__box_number=box_number)

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
