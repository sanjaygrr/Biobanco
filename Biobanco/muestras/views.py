from .models import Storage, StorageType, Sample, Location, Shipment
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models import Q, Prefetch
from django.contrib.auth import login
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse
from accounts.models import Account
from django.contrib import messages
from django.urls import reverse
import json


def home(request):
    num_shipments = Shipment.objects.count()
    num_freezers_enabled = Storage.objects.filter(
        STORAGE_TYPE_id_storagetype__name_storagetype=3, storage_state=True).count()
    num_freezers_disabled = Storage.objects.filter(
        STORAGE_TYPE_id_storagetype__name_storagetype=3, storage_state=False).count()

    # Agregar la consulta para contar muestras con SHIPMENT_id_shipment igual a 0
    num_samples = Sample.objects.filter(SHIPMENT_id_shipment=0).count()

    # Obtén el nombre de usuario del usuario actualmente autenticado
    user_name = request.user.username if request.user.is_authenticated else 'Invitado'

    context = {
        'num_freezers_enabled': num_freezers_enabled,
        'num_freezers_disabled': num_freezers_disabled,
        'num_samples': num_samples,
        'num_shipments': num_shipments,
        # Agrega el nuevo valor al contexto
        'user_name': user_name,  # Agrega el nombre de usuario al contexto
    }

    return render(request, 'home.html', context)


def signup(request):
    if request.method == 'POST':
        try:
            user = Account.objects.create_user(
                email=request.POST['email'],
                username=request.POST['username'],
                password=request.POST['password']
            )
            user.save()
            login(request, user)  # Inicia sesión al usuario
            # Renderizar la misma plantilla con un mensaje de éxito
            return render(request, 'signup.html', {'success': 'Usuario creado exitosamente. Ahora estás autenticado.'})
        except IntegrityError:
            # Mostrar mensaje de error si hay un problema
            return render(request, 'signup.html', {'error': 'El correo ya existe'})
    else:
        return render(request, 'signup.html')


def user_list(request):
    search_query = request.GET.get('search')
    if search_query:
        users = Account.objects.filter(username__icontains=search_query) | Account.objects.filter(
            email__icontains=search_query)
    else:
        users = Account.objects.all()

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

            # Check if there are associated samples in this space
            if status is False:  # If trying to disable the space
                has_samples = Location.objects.filter(
                    STORAGE_id_storage_1=storage).exists()
                if has_samples:
                    return JsonResponse({'error': 'No se puede deshabilitar el espacio porque contiene muestras.'}, status=400)

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

                # Verificar si hay muestras en este espacio (Location)
                has_samples = Location.objects.filter(
                    STORAGE_id_storage_1=storage).exists()
                if has_samples:
                    return JsonResponse({'error': 'No se puede eliminar el espacio porque contiene muestras.'}, status=400)

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
        id_subject = request.POST.get('id_subject')
        date_sample = request.POST.get('date_sample')
        ml_volume = float(request.POST.get('ml_volume'))
        state_analysis = request.POST.get('state_analysis') == "1"
        state_preservation = request.POST.get('state_preservation') == "1"
        specification = request.POST.get('specification')
        shipment_id = request.POST.get('SHIPMENT_id_shipment')

        sample = Sample(
            id_subject=id_subject,
            date_sample=date_sample,
            ml_volume=ml_volume,
            state_analysis=state_analysis,
            state_preservation=state_preservation,
            specification=specification
        )
        storage_combination = f"{request.POST.get('freezer_id')}-{request.POST.get('rack_id')}-{request.POST.get('caja_id')}"
        cell_value = int(request.POST.get('cell'))

        existing_location = Location.objects.filter(
            STORAGE_id_storage_1__storage_name=storage_combination,
            cell=cell_value
        ).first()

        if existing_location:
            # Si existe una ubicación en el mismo espacio, muestra una alerta de SweetAlert
            return JsonResponse({'message': 'No se puede crear muestra en el mismo espacio repetida'}, status=400)

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

        action = request.POST.get('action')
        if action == "add_another":
            return redirect('create_sample')
        else:
            return redirect('sample_list')

    else:
        storages = Storage.objects.all().order_by('storage_name')
        storage_types = StorageType.objects.all().order_by('name_storagetype')

        context = {
            'storages': storages,
            'storage_types': storage_types
        }

        return render(request, 'create_sample.html', context)


@csrf_exempt
def sample_list(request):

    samples = Sample.objects.all()

    if request.method == "GET":
        subject_id = request.GET.get('subject_id')
        sample_date = request.GET.get('sample_date')
        freezer_number = request.GET.get('freezer_number')
        rack_number = request.GET.get('rack_number')
        box_number = request.GET.get('box_number')
        sample_id = request.GET.get('sample_id')
        cell = request.GET.get('cell')

        if subject_id:
            samples = samples.filter(id_subject=subject_id)
        if sample_date:
            samples = samples.filter(date_sample=sample_date)
        if freezer_number:
            samples = samples.filter(location__STORAGE_id_storage_1__storage_name=freezer_number,
                                     location__STORAGE_TYPE_id_storagetype__name_storagetype=1)
        if rack_number:
            samples = samples.filter(location__STORAGE_id_storage_1__storage_name=rack_number,
                                     location__STORAGE_TYPE_id_storagetype__name_storagetype=2)
        if box_number:
            samples = samples.filter(location__STORAGE_id_storage_1__storage_name=box_number,
                                     location__STORAGE_TYPE_id_storagetype__name_storagetype=3)
        if sample_id:
            samples = samples.filter(id_sample__icontains=sample_id)
        if cell:
            samples = samples.filter(location__cell=cell)

        # Añadir información de ubicación a cada muestra
        for sample in samples:
            freezer_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype__name_storagetype=1).first()
            sample.freezer_name = freezer_location.STORAGE_id_storage_1.storage_name if freezer_location else 'No Asignado'

            rack_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype__name_storagetype=2).first()
            sample.rack_name = rack_location.STORAGE_id_storage_1.storage_name if rack_location else 'No Asignado'

            box_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype__name_storagetype=3).first()
            sample.box_name = box_location.STORAGE_id_storage_1.storage_name if box_location else 'No Asignado'

    storages = Storage.objects.all().order_by('storage_name')
    storage_types = StorageType.objects.all().order_by('name_storagetype')

    context = {
        'samples': samples,
        'storages': storages,
        'storage_types': storage_types
    }

    return render(request, 'sample_list.html', context)


@csrf_exempt
@require_POST
def update_sample(request, sample_id):
    try:
        data = json.loads(request.body)
        sample = Sample.objects.get(pk=sample_id)

        # Actualización de los datos básicos de la muestra
        sample.state_preservation = data.get('state_preservation')
        sample.save()

        # Actualización de las ubicaciones
        for storage_type_id, storage_id in [('3', 'freezer_id'), ('2', 'rack_id'), ('1', 'box_id')]:
            storage_value = data.get(storage_id)
            if storage_value:
                location = Location.objects.filter(
                    SAMPLE_id_sample_1=sample,
                    STORAGE_TYPE_id_storagetype_id=storage_type_id
                ).first()
                if location:
                    location.STORAGE_id_storage_1_id = storage_value
                    # Actualizar celda si es necesario
                    location.cell = data.get('cell', location.cell)
                    location.save()
                else:
                    # Crear una nueva entrada si no existe
                    new_location = Location(
                        SAMPLE_id_sample_1=sample,
                        STORAGE_id_storage_1_id=storage_value,
                        STORAGE_TYPE_id_storagetype_id=storage_type_id,
                        # Usar un valor predeterminado o el proporcionado
                        cell=data.get('cell', 0)
                    )
                    new_location.save()

        return JsonResponse({'status': 'success', 'message': 'Sample updated successfully.'})
    except Sample.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Sample not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def delete_sample(request, sample_id):
    try:
        sample = Sample.objects.get(pk=sample_id)
        sample.delete()
        return JsonResponse({'status': 'success', 'message': 'Sample deleted successfully.'})
    except Sample.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Sample not found.'}, status=404)


def trazability(request):
    return render(request, 'trazability.html')


@require_http_methods(["GET", "POST"])
def shipments(request):
    if request.method == 'POST':
        # Aquí puedes añadir más validaciones si es necesario
        date_shipment = request.POST.get('date_shipment')
        laboratory = request.POST.get('laboratory')
        analysis = request.POST.get('analysis')

        # Crear y guardar el nuevo Shipment
        shipment = Shipment(
            date_shipment=date_shipment,
            laboratory=laboratory,
            analysis=analysis
        )
        shipment.save()

        # Redirige a la vista de selección de muestras
        return redirect('shipments_select')  # Usa el nombre de la ruta

    # Si es un GET, simplemente renderiza la página con el formulario
    return render(request, 'shipments.html')


def login_screen(request):
    return render(request, 'login_screen.html')


def create_password(request):
    return render(request, 'create_password.html')


@require_http_methods(["GET", "POST"])
def shipments_select(request):
    samples = Sample.objects.all().prefetch_related('location_set')
    selected_samples = []

    if request.method == 'POST':
        if 'filter_action' in request.POST:
            # Procesar el formulario de filtro
            year = request.POST.get('year')
            month = request.POST.get('month')
            subject_id = request.POST.get('subject_id')
            volume_condition = request.POST.get('volume_condition')
            volume = request.POST.get('volume')

            if volume_condition and volume:
                # Aplicar el filtro de volumen según la condición seleccionada
                if volume_condition == 'greater':
                    samples = samples.filter(ml_volume__gt=float(volume))
                elif volume_condition == 'less':
                    samples = samples.filter(ml_volume__lt=float(volume))
                elif volume_condition == 'equal':
                    samples = samples.filter(ml_volume=float(volume))

            if year:
                samples = samples.filter(date_sample__year=year)
            if month:
                samples = samples.filter(date_sample__month=month)
            if subject_id:
                samples = samples.filter(id_subject=subject_id)

    # Este bloque maneja la acción de GET
    # Añadir información de ubicación a cada muestra
    for sample in samples:
        freezer_location = sample.location_set.filter(
            STORAGE_TYPE_id_storagetype_id=1).first()  # ID para freezer
        sample.freezer_name = freezer_location.STORAGE_id_storage_1.storage_name if freezer_location else 'No Asignado'

        rack_location = sample.location_set.filter(
            STORAGE_TYPE_id_storagetype_id=2).first()  # ID para rack
        sample.rack_name = rack_location.STORAGE_id_storage_1.storage_name if rack_location else 'No Asignado'

        box_location = sample.location_set.filter(
            STORAGE_TYPE_id_storagetype_id=3).first()  # ID para caja
        sample.box_name = box_location.STORAGE_id_storage_1.storage_name if box_location else 'No Asignado'

    return render(request, 'shipments_select.html', {'samples': samples})


@csrf_exempt
@require_POST
def update_samples_shipment(request):
    try:
        # Decodifica el cuerpo de la solicitud
        data = json.loads(request.body.decode('utf-8'))
        sample_ids = data.get('sample_ids')

        if not sample_ids:
            return JsonResponse({'error': 'Faltan datos necesarios'}, status=400)

        # Obtener el último Shipment creado
        last_shipment = Shipment.objects.last()
        if not last_shipment:
            return JsonResponse({'error': 'No se encontró ningún envío'}, status=404)

        # Actualizar los espacios para cada muestra
        for sample_id in sample_ids:
            sample = Sample.objects.get(id_sample=sample_id)
            sample.SHIPMENT_id_shipment = last_shipment.id_shipment
            sample.save()

        return JsonResponse({'message': 'Espacios actualizados con éxito'})

    except Sample.DoesNotExist:
        return JsonResponse({'error': 'Una o más muestras no encontradas'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)


def shipments_report(request):
    laboratories = Shipment.objects.values_list(
        'laboratory', flat=True).distinct()
    users = Account.objects.all()

    # Inicia con todos los envíos
    shipments = Shipment.objects.all()

    # Aplica filtros solo si se proporcionan valores
    sender_filter = request.GET.get('sender')
    date_filter = request.GET.get('date')
    laboratory_filter = request.GET.get('laboratory')

    if sender_filter:
        # Filtra por el remitente si se proporciona un valor
        shipments = shipments.filter(created_by_id=sender_filter)

    if date_filter:
        # Filtra por la fecha si se proporciona un valor
        shipments = shipments.filter(date_shipment=date_filter)

    if laboratory_filter:
        # Filtra por laboratorio si se proporciona un valor
        shipments = shipments.filter(laboratory=laboratory_filter)

    # Aplica el conteo de muestras a cada envío
    for shipment in shipments:
        shipment.num_samples = Sample.objects.filter(
            SHIPMENT_id_shipment=shipment.id_shipment).count()

    context = {
        'shipments': shipments,
        'laboratories': laboratories,
        'users': users,
    }

    return render(request, 'shipments_report.html', context)


def samples_report(request):
    samples = Sample.objects.all()

    if request.method == "GET":
        subject_id = request.GET.get('subject_id')
        sample_date = request.GET.get('sample_date')
        freezer_number = request.GET.get('freezer_number')
        rack_number = request.GET.get('rack_number')
        box_number = request.GET.get('box_number')
        sample_id = request.GET.get('sample_id')
        cell = request.GET.get('cell')

        if subject_id:
            samples = samples.filter(id_subject=subject_id)
        if sample_date:
            samples = samples.filter(date_sample=sample_date)
        if freezer_number:
            samples = samples.filter(location__STORAGE_id_storage_1__storage_name=freezer_number,
                                     location__STORAGE_TYPE_id_storagetype__name_storagetype=1)
        if rack_number:
            samples = samples.filter(location__STORAGE_id_storage_1__storage_name=rack_number,
                                     location__STORAGE_TYPE_id_storagetype__name_storagetype=2)
        if box_number:
            samples = samples.filter(location__STORAGE_id_storage_1__storage_name=box_number,
                                     location__STORAGE_TYPE_id_storagetype__name_storagetype=3)
        if sample_id:
            samples = samples.filter(id_sample__icontains=sample_id)
        if cell:
            samples = samples.filter(location__cell=cell)

        # Añadir información de ubicación a cada muestra
        for sample in samples:
            freezer_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype__name_storagetype=1).first()
            sample.freezer_name = freezer_location.STORAGE_id_storage_1.storage_name if freezer_location else 'No Asignado'

            rack_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype__name_storagetype=2).first()
            sample.rack_name = rack_location.STORAGE_id_storage_1.storage_name if rack_location else 'No Asignado'

            box_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype__name_storagetype=3).first()
            sample.box_name = box_location.STORAGE_id_storage_1.storage_name if box_location else 'No Asignado'

    storages = Storage.objects.all().order_by('storage_name')
    storage_types = StorageType.objects.all().order_by('name_storagetype')

    context = {
        'samples': samples,
        'storages': storages,
        'storage_types': storage_types
    }

    return render(request, 'samples_report.html', context)


def shipments_detail(request, shipment_id):
    # Obtiene el envío por su ID o devuelve una página de error 404 si no se encuentra
    shipment = get_object_or_404(Shipment, pk=shipment_id)

    # Obtiene todas las muestras asociadas con este envío
    samples = Sample.objects.filter(SHIPMENT_id_shipment=shipment_id)

    context = {
        'shipment': shipment,
        'samples': samples,
    }

    return render(request, 'shipments_detail.html', context)
