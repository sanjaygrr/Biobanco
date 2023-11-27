from .models import Storage, StorageType, Sample, Location, Shipment, SampleEvent
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models import Q, Prefetch
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseNotFound
from accounts.models import Account, Role
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
import logging
import json
from django.utils import timezone
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

# para errores en URL


@login_required
def custom_not_found_view(request, exception):
    if request.user.is_authenticated:

        return render(request, 'login', status=404)
    else:

        logout(request)

        return redirect('login')


def login_screen(request):

    message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:

            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))

            else:
                return redirect('home')  # redirecciona al home de biobanco

        else:
            messages.error(request, 'Usuario y/o Password incorrecto(s)')

            return render(request, 'login_screen.html')

    # si usuario no está autenticado
    if not request.user.is_authenticated and 'next' in request.GET:

        messages.info(
            request, 'Debes estar autenticado para acceder a esta página')

    return render(request, 'login_screen.html')


@login_required
def logout_screen(request):
    logout(request)
    # request.session['logout_message'] = "You have been logged out successfully."

    return redirect('login')


@login_required
def redirect_login(request):

    return redirect(request, 'login_screen.html')


@login_required
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


@login_required
def signup(request):
    if request.method == 'POST':
        try:
            # Crear el usuario sin el rol
            user = Account.objects.create_user(
                email=request.POST['email'],
                username=request.POST['username'],
                name=request.POST['name'],
                lastname=request.POST['lastname'],
                password=request.POST['password']
            )

            # Asignar el rol y guardar el usuario
            role_id = request.POST.get('role', Role.ADMIN)
            user.ROLE_id_role = Role.objects.get(id_role=role_id)
            user.is_staff = True
            user.is_admin = True
            user.is_superuser = True
            user.save()

            return render(request, 'signup.html', {'success': 'Usuario creado exitosamente.'})
        except IntegrityError:
            return render(request, 'signup.html', {'error': 'El correo ya existe'})
    else:
        return render(request, 'signup.html')


@login_required
def user_list(request):
    search_query = request.GET.get('search')
    if search_query:
        users = Account.objects.filter(username__icontains=search_query) | Account.objects.filter(
            email__icontains=search_query)
    else:
        users = Account.objects.all()

    return render(request, 'user_list.html', {'users': users})


@login_required
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


@login_required
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
@login_required
@require_POST
def update_space_status(request):
    try:
        data = json.loads(request.body)
        if not all(isinstance(space_id, str) and isinstance(status, bool) for space_id, status in data['changes'].items()):
            return JsonResponse({'error': 'Formato de datos inválido'}, status=400)

        success_messages = []
        error_messages = []

        for space_id, status in data['changes'].items():
            storage = Storage.objects.get(pk=space_id)

            # Check if there are associated samples in this space
            if status is False:  # If trying to disable the space
                has_samples_with_shipment_0 = Location.objects.filter(
                    STORAGE_id_storage_1=storage, SAMPLE_id_sample_1__SHIPMENT_id_shipment=0).exists()

                if has_samples_with_shipment_0:
                    error_messages.append(
                        f'No se puede deshabilitar el espacio {storage.storage_name} porque contiene muestras')
                else:
                    storage.storage_state = status
                    storage.save()
                    success_messages.append(
                        f'El espacio {storage.storage_name} ha sido deshabilitado con éxito.')
            else:
                storage.storage_state = status
                storage.save()
                success_messages.append(
                    f'El espacio {storage.storage_name} ha sido habilitado con éxito.')

        return JsonResponse({'success_messages': success_messages, 'error_messages': error_messages})

    except Storage.DoesNotExist:
        return JsonResponse({'error_messages': ['Espacio no encontrado']}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error_messages': ['Datos JSON inválidos']}, status=400)
    except ValueError as ve:
        return JsonResponse({'error_messages': [f'Error de valor: {str(ve)}']}, status=400)
    except Exception as e:
        return JsonResponse({'error_messages': [f'Error inesperado: {str(e)}']}, status=500)


@csrf_exempt
@login_required
@require_POST
def delete_spaces(request):
    try:
        data = json.loads(request.body)
        print("Received data:", data)
        success_messages = []
        error_messages = []

        for space_id, should_delete in data.items():
            if should_delete:
                storage = Storage.objects.get(pk=space_id)

                # Verificar si hay muestras en este espacio (Location)
                has_samples = Location.objects.filter(
                    STORAGE_id_storage_1=storage).exists()
                if has_samples:
                    error_messages.append(
                        f'No se puede eliminar el espacio {storage.storage_name} porque contiene muestras.')
                else:
                    storage.delete()
                    success_messages.append(
                        f'El espacio {storage.storage_name} ha sido eliminado con éxito.')

        return JsonResponse({'success_messages': success_messages, 'error_messages': error_messages})

    except Storage.DoesNotExist:
        return JsonResponse({'error_messages': ['Espacio no encontrado']}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error_messages': ['Datos JSON inválidos']}, status=400)
    except Exception as e:
        return JsonResponse({'error_messages': [str(e)]}, status=500)


@login_required
def is_valid_int(value):
    """Función de ayuda para comprobar si un valor puede ser convertido a int."""
    try:
        int(value)
        return True
    except ValueError:
        return False


@login_required
def create_sample(request):
    print("Entrando a la función create_sample")
    if request.method == "POST":
        id_subject = request.POST.get('id_subject')
        date_sample = request.POST.get('date_sample')
        ml_volume = float(request.POST.get('ml_volume'))
        state_analysis = request.POST.get('state_analysis') == "1"
        state_preservation = request.POST.get('state_preservation') == "1"
        specification = request.POST.get('specification')
        shipment_id = request.POST.get('SHIPMENT_id_shipment')
        cell_value = int(request.POST.get('cell'))

        # Verificar si la celda específica en la caja está ocupada
        caja_value = request.POST.get('caja_id')
        if caja_value:
            _, caja_name = caja_value.split('-')
            caja_obj = Storage.objects.filter(storage_name=caja_name).first()
            if caja_obj:
                existing_location = Location.objects.filter(
                    STORAGE_id_storage_1=caja_obj,
                    cell=cell_value,
                    # SAMPLE_id_sample_1__SHIPMENT_id_shipment
                ).first()
                if existing_location:
                    print(
                        f"La celda {cell_value} en caja {caja_obj.storage_name} ya está ocupada.")
                    return JsonResponse({'message': f'La celda {cell_value} en caja {caja_obj.storage_name} ya está ocupada'}, status=400)

        with transaction.atomic():
            sample = Sample(
                id_subject=id_subject,
                date_sample=date_sample,
                ml_volume=ml_volume,
                state_analysis=state_analysis,
                state_preservation=state_preservation,
                specification=specification,
                SHIPMENT_id_shipment=0
            )

            existing_sample = Sample.objects.filter(
                id_subject=id_subject,
                date_sample=date_sample,
                ml_volume=ml_volume,
                state_preservation=state_preservation,
                specification=specification,
                SHIPMENT_id_shipment=0
            ).first()
            if existing_sample:
                return JsonResponse({'message': 'Ya existe una muestra con los mismos detalles proporcionados'}, status=400)

            sample.save()
            print(f"Muestra guardada con id_sample: {sample.id_sample}")

            # Creación y guardado de SampleEvent
            event_user = request.user.username
            action_information = f"ID de la muestra: {sample.id_sample}"
            sample_event = SampleEvent(
                event_user=event_user,
                event_date=timezone.now(),
                action="Registrar muestra",
                action_information=action_information,
                SAMPLE_id_sample=sample
            )
            sample_event.save()

            # Lógica de Guardado de Ubicaciones
            for storage_value_key in ['freezer_id', 'rack_id', 'caja_id']:
                storage_value = request.POST.get(storage_value_key)
                if storage_value:
                    storage_type, storage_name = storage_value.split('-')
                    storage_obj = Storage.objects.filter(
                        storage_name=storage_name).first()
                    if storage_obj:
                        location = Location(
                            cell=cell_value,
                            SAMPLE_id_sample_1=sample,
                            STORAGE_id_storage_1=storage_obj,
                            STORAGE_TYPE_id_storagetype_id=int(storage_type)
                        )
                        location.save()
                        if location.id_location:
                            print(
                                f"Ubicación para {storage_obj.storage_name} guardada con éxito, id_location: {location.id_location}")

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
@login_required
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
                                     location__STORAGE_TYPE_id_storagetype__name_storagetype=3)
        if rack_number:
            samples = samples.filter(location__STORAGE_id_storage_1__storage_name=rack_number,
                                     location__STORAGE_TYPE_id_storagetype__name_storagetype=2)
        if box_number:
            samples = samples.filter(location__STORAGE_id_storage_1__storage_name=box_number,
                                     location__STORAGE_TYPE_id_storagetype__name_storagetype=1)
        if sample_id:
            samples = samples.filter(id_sample__icontains=sample_id)
        if cell:
            samples = samples.filter(location__cell=cell)

        # Añadir información de ubicación a cada muestra
        for sample in samples:
            freezer_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype__name_storagetype=3).first()
            sample.freezer_name = freezer_location.STORAGE_id_storage_1.storage_name if freezer_location else 'No Asignado'

            rack_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype__name_storagetype=2).first()
            sample.rack_name = rack_location.STORAGE_id_storage_1.storage_name if rack_location else 'No Asignado'

            box_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype__name_storagetype=1).first()
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
@login_required
@require_POST
@transaction.atomic
def update_sample(request, sample_id):
    try:
        data = json.loads(request.body)
        sample = get_object_or_404(Sample, id_sample=sample_id)

        # Actualizar el estado de preservación
        state_preservation = data.get('state_preservation') == "1"
        sample.state_preservation = state_preservation
        sample.save()

        storage_mappings = {
            'freezer_id': '3',  # Asumiendo que 3 es para Freezer
            'rack_id': '2',     # Asumiendo que 2 es para Rack
            'box_id': '1'       # Asumiendo que 1 es para Caja
        }

        cell_value = int(data.get('cell'))

        for storage_key, expected_storage_type_id in storage_mappings.items():
            storage_value = data.get(storage_key)
            if storage_value:
                storage_type_id, storage_name = storage_value.split('-')

                if storage_type_id != expected_storage_type_id:
                    return JsonResponse({'error': f'Tipo de almacenamiento incorrecto para {storage_key}'}, status=400)

                storage_type = StorageType.objects.get(
                    name_storagetype=storage_type_id)
                storage = Storage.objects.get(
                    STORAGE_TYPE_id_storagetype=storage_type, storage_name=storage_name)

                # Verificar si la celda está ocupada
                if storage_key == 'box_id':
                    existing_location = Location.objects.exclude(SAMPLE_id_sample_1=sample).filter(
                        STORAGE_id_storage_1=storage,
                        cell=cell_value
                    ).first()
                    if existing_location:
                        return JsonResponse({'error': f'La celda {cell_value} en caja {storage_name} ya está ocupada'}, status=400)

                # Actualizar la ubicación existente
                location = Location.objects.filter(
                    SAMPLE_id_sample_1=sample,
                    STORAGE_TYPE_id_storagetype=storage_type
                ).first()

                if location:
                    location.STORAGE_id_storage_1 = storage
                    location.cell = cell_value
                    location.save()
                else:
                    return JsonResponse({'error': f'Ubicación no encontrada para el tipo de almacenamiento: {storage_type_id}'}, status=404)

        # Registrar el evento (opcional)
        event_user = request.user.username
        action_information = f"ID de la muestra: {sample.id_sample}"
        SampleEvent.objects.create(
            event_user=event_user,
            event_date=timezone.now(),
            action="Actualizar muestra",
            action_information=action_information,
            SAMPLE_id_sample=sample
        )

        return JsonResponse({'status': 'success'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error al decodificar JSON'}, status=400)
    except Sample.DoesNotExist:
        return JsonResponse({'error': 'Muestra no encontrada'}, status=404)
    except StorageType.DoesNotExist:
        return JsonResponse({'error': 'Tipo de almacenamiento no encontrado'}, status=404)
    except Storage.DoesNotExist:
        return JsonResponse({'error': 'Almacenamiento no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
@require_POST
@transaction.atomic
def delete_sample(request, sample_id):
    try:
        print(
            f"Iniciando proceso de eliminación para la muestra con ID {sample_id}.")
        sample = Sample.objects.get(pk=sample_id)
        print(f"Muestra encontrada: {sample}")

        # Crear y guardar el SampleEvent antes de eliminar la muestra
        sample_event = SampleEvent(
            event_user=request.user.username,
            event_date=timezone.now(),
            action="Eliminar muestra",
            action_information=f"Muestra con ID {sample_id} eliminada",
            SAMPLE_id_sample=sample
        )
        sample_event.save()
        print(f"SampleEvent creado con éxito: {sample_event.id_event}")

        sample.delete()
        print(f"Muestra eliminada con éxito.")

        return JsonResponse({'status': 'success', 'message': 'Sample deleted successfully.'})

    except Sample.DoesNotExist as e:
        print(f"Error: la muestra con ID {sample_id} no existe. {e}")
        return JsonResponse({'status': 'error', 'message': 'Sample not found.'}, status=404)
    except Exception as e:
        print(
            f"Error inesperado al eliminar la muestra con ID {sample_id}: {e}")
        return JsonResponse({'error_messages': [str(e)]}, status=500)


@login_required
def trazability(request):
    # Recupera los parámetros de búsqueda de request.GET
    subject_id = request.GET.get('subject_id')
    sample_date = request.GET.get('sample_date')
    sample_number = request.GET.get('sample_number')

    # Filtra los objetos SampleEvent en función de los parámetros de búsqueda
    sample_events = SampleEvent.objects.all()

    if subject_id:
        if len(subject_id) == 1:
            sample_events = sample_events.filter(event_user=subject_id)
        else:
            sample_events = sample_events.filter(
                event_user__contains=subject_id)

    if sample_date:
        sample_events = sample_events.filter(event_date=sample_date)

    if sample_number:
        sample_events = sample_events.filter(
            action_information__icontains=sample_number)

    # Pasa los objetos filtrados al contexto de la plantilla
    context = {'sample_events': sample_events}
    return render(request, 'trazability.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def shipments(request):
    if request.method == 'POST':
        # Recolección de datos del formulario
        date_shipment = request.POST.get('date_shipment')
        laboratory = request.POST.get('laboratory')
        analysis = request.POST.get('analysis')

        # Crear y guardar el nuevo Shipment
        shipment = Shipment(
            date_shipment=date_shipment,
            laboratory=laboratory,
            analysis=analysis,
            sender=request.user  # Asignar el usuario actual como remitente
        )
        shipment.save()

        # Obtener la última muestra guardada
        # Asumiendo que 'id_sample' es la clave principal
        last_sample = Sample.objects.latest('id_sample')

        # Crear y guardar el SampleEvent
        sample_event = SampleEvent(
            # Asumiendo que quieres registrar el usuario que realiza la acción
            event_user=request.user.username,
            event_date=timezone.now(),  # Fecha actual
            action="Crear envío",  # Acción realizada
            action_information=f"Envío creado a laboratorio {shipment.laboratory}",
            SAMPLE_id_sample=last_sample
        )
        sample_event.save()

        # Redirigir a la vista de selección de muestras
        # Asegúrate de que 'shipments_select' es el nombre correcto de la ruta
        return redirect('shipments_select')

    # Si es un GET, renderiza la página con el formulario
    return render(request, 'shipments.html')


@login_required
def create_password(request):
    return render(request, 'create_password.html')


@login_required
@require_http_methods(["GET", "POST"])
def shipments_select(request):
    if request.method == 'POST':
        # Verificar si es una solicitud AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Manejo de la petición AJAX
            data = json.loads(request.body)
            year = data.get('year')
            month = data.get('month')
            subject_id = data.get('subject_id')
            volume_condition = data.get('volume_condition')
            volume = data.get('volume')

            samples = Sample.objects.all()
            # Filtros basados en los datos recibidos
            if year:
                samples = samples.filter(date_sample__year=year)
            if month:
                samples = samples.filter(date_sample__month=month)
            if subject_id:
                samples = samples.filter(id_subject=subject_id)
            if volume_condition and volume:
                if volume_condition == 'greater':
                    samples = samples.filter(ml_volume__gt=volume)
                elif volume_condition == 'less':
                    samples = samples.filter(ml_volume__lt=volume)
                elif volume_condition == 'equal':
                    samples = samples.filter(ml_volume=volume)

            samples_data = list(samples.values(
                'id_sample', 'id_subject', 'date_sample',
                'ml_volume', 'state_preservation'
                # Añade otros campos necesarios
            ))

            return JsonResponse({'samples': samples_data})

        else:
            # Manejo de la acción POST no AJAX
            year = request.POST.get('year')
            month = request.POST.get('month')
            subject_id = request.POST.get('subject_id')
            volume_condition = request.POST.get('volume_condition')
            volume = request.POST.get('volume')

            samples = Sample.objects.all()
            if year:
                samples = samples.filter(date_sample__year=year)
            if month:
                samples = samples.filter(date_sample__month=month)
            if subject_id:
                samples = samples.filter(id_subject=subject_id)
            if volume_condition and volume:
                if volume_condition == 'greater':
                    samples = samples.filter(ml_volume__gt=float(volume))
                elif volume_condition == 'less':
                    samples = samples.filter(ml_volume__lt=float(volume))
                elif volume_condition == 'equal':
                    samples = samples.filter(ml_volume=float(volume))

    else:
        # Manejo de la acción GET no AJAX
        samples = Sample.objects.all().prefetch_related('location_set')

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
@login_required
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
            sample.state_preservation = "1"
            sample.state_analysis = "1"
            sample.save()

        return JsonResponse({'message': '¡Muestras para envío registradas con éxito! '})

    except Sample.DoesNotExist:
        return JsonResponse({'error': 'Una o más muestras no encontradas'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)


@login_required
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
        shipments = shipments.filter(sender_id=sender_filter)

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


@login_required
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
                                     location__STORAGE_TYPE_id_storagetype__name_storagetype=3)
        if rack_number:
            samples = samples.filter(location__STORAGE_id_storage_1__storage_name=rack_number,
                                     location__STORAGE_TYPE_id_storagetype__name_storagetype=2)
        if box_number:
            samples = samples.filter(location__STORAGE_id_storage_1__storage_name=box_number,
                                     location__STORAGE_TYPE_id_storagetype__name_storagetype=1)
        if sample_id:
            samples = samples.filter(id_sample__icontains=sample_id)
        if cell:
            samples = samples.filter(location__cell=cell)

        # Añadir información de ubicación a cada muestra
        for sample in samples:
            freezer_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype__name_storagetype=3).first()
            sample.freezer_name = freezer_location.STORAGE_id_storage_1.storage_name if freezer_location else 'No Asignado'

            rack_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype__name_storagetype=2).first()
            sample.rack_name = rack_location.STORAGE_id_storage_1.storage_name if rack_location else 'No Asignado'

            box_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype__name_storagetype=1).first()
            sample.box_name = box_location.STORAGE_id_storage_1.storage_name if box_location else 'No Asignado'

    storages = Storage.objects.all().order_by('storage_name')
    storage_types = StorageType.objects.all().order_by('name_storagetype')

    context = {
        'samples': samples,
        'storages': storages,
        'storage_types': storage_types
    }

    return render(request, 'samples_report.html', context)


@login_required
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
