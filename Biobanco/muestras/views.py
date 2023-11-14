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
    return render(request, 'home.html')


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
            return redirect('sample_list')

    else:
        # Cargar datos para el formulario
        storages = Storage.objects.all().order_by('storage_name')
        storage_types = StorageType.objects.all().order_by('name_storagetype')

        context = {
            'storages': storages,
            'storage_types': storage_types
        }

        return render(request, 'create_sample.html', context)


@csrf_exempt
def sample_list(request):
    samples = Sample.objects.all().prefetch_related('location_set')

    if request.method == "GET":
        subject_id = request.GET.get('subject_id')
        sample_date = request.GET.get('sample_date')
        freezer_number = request.GET.get('freezer_number')
        rack_number = request.GET.get('rack_number')
        box_number = request.GET.get('box_number')

        # Aplicar filtros si se proporcionan
        if subject_id:
            samples = samples.filter(id_subject=subject_id)
        if sample_date:
            samples = samples.filter(date_sample=sample_date)
        if freezer_number:
            samples = samples.filter(location_set__STORAGE_id_storage_1__storage_name=freezer_number,
                                     location_set__STORAGE_TYPE_id_storagetype__name_storagetype=3)
        if rack_number:
            samples = samples.filter(location_set__STORAGE_id_storage_1__storage_name=rack_number,
                                     location_set__STORAGE_TYPE_id_storagetype__name_storagetype=2)
        if box_number:
            samples = samples.filter(location_set__STORAGE_id_storage_1__storage_name=box_number,
                                     location_set__STORAGE_TYPE_id_storagetype__name_storagetype=1)

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
def edit_sample(request, sample_id):
    if request.method == 'POST':
        # Convertir el cuerpo de la solicitud JSON a un diccionario Python
        data = json.loads(request.body)

        # Obtener la muestra por su ID
        sample = get_object_or_404(Sample, pk=sample_id)

        # Actualizar los campos de la muestra
        sample.state_preservation = data.get('state_preservation') == '1'
        sample.save()

        # Obtener y actualizar las ubicaciones
        # Nota: Asegúrate de que estos campos existan en tu modelo y se ajusten a tus necesidades
        freezer_id = data.get('freezer_id')
        rack_id = data.get('rack_id')
        box_id = data.get('box_id')
        cell = data.get('cell')

        # Actualizar Freezer
        if freezer_id:
            location_freezer = Location.objects.filter(
                SAMPLE_id_sample_1=sample, STORAGE_TYPE_id_storagetype__name_storagetype=3).first()
            if location_freezer:
                location_freezer.STORAGE_id_storage_1_id = freezer_id
                location_freezer.cell = cell
                location_freezer.save()

        # Actualizar Rack
        if rack_id:
            location_rack = Location.objects.filter(
                SAMPLE_id_sample_1=sample, STORAGE_TYPE_id_storagetype__name_storagetype=2).first()
            if location_rack:
                location_rack.STORAGE_id_storage_1_id = rack_id
                location_rack.cell = cell
                location_rack.save()

        # Actualizar Box
        if box_id:
            location_box = Location.objects.filter(
                SAMPLE_id_sample_1=sample, STORAGE_TYPE_id_storagetype__name_storagetype=1).first()
            if location_box:
                location_box.STORAGE_id_storage_1_id = box_id
                location_box.cell = cell
                location_box.save()

        # Devuelve una respuesta JSON indicando éxito
        return JsonResponse({'status': 'success', 'message': 'Muestra actualizada con éxito'})

    else:
        # Manejar otros métodos HTTP, si es necesario
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


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

        # Puedes usar el sistema de mensajes para enviar confirmaciones o errores
        messages.success(request, 'Envío registrado con éxito.')

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
    if request.method == 'POST':
        if 'filter_action' in request.POST:
            year = request.POST.get('year')
            month = request.POST.get('month')
            subject_id = request.POST.get('subject_id')
            volume_condition = request.POST.get('volume_condition')
            volume = request.POST.get('volume')

            samples = Sample.objects.all().prefetch_related('location_set')
            if year:
                samples = samples.filter(date_sample__year=year)
            if month:
                samples = samples.filter(date_sample__month=month)
            if subject_id:
                samples = samples.filter(id_subject=subject_id)
            # Implementar lógica para el volumen según 'volume_condition' y 'volume'

        elif 'register_action' in request.POST:
            selected_samples = request.POST.getlist('selected_samples')
            if not selected_samples:
                messages.error(
                    request, 'No se seleccionaron muestras para el envío.')
                return redirect('shipments_select')

            # Asumiendo que tienes un input para la fecha, laboratorio y análisis en tu formulario
            date_shipment = request.POST.get('date_shipment')
            laboratory = request.POST.get('laboratory')
            analysis = request.POST.get('analysis')

            # Crea un nuevo Shipment
            new_shipment = Shipment.objects.create(
                date_shipment=date_shipment,
                laboratory=laboratory,
                analysis=analysis
            )

            # Actualiza el SHIPMENT_id_shipment de las muestras seleccionadas
            Sample.objects.filter(id_sample__in=selected_samples).update(
                SHIPMENT_id_shipment=new_shipment.id_shipment
            )

            messages.success(
                request, f'El envío ha sido registrado con éxito. ID de envío: {new_shipment.id_shipment}')
            # No rediriges a una nueva URL, simplemente vuelves a cargar la página con el mensaje de confirmación
            return redirect('shipments_select')

    else:
        # Este bloque maneja la acción de GET
        samples = Sample.objects.all().prefetch_related('location_set')

        # Añadir información de ubicación a cada muestra
        for sample in samples:
            freezer_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype_id=3).first()  # ID para freezer
            sample.freezer_name = freezer_location.STORAGE_id_storage_1.storage_name if freezer_location else 'No Asignado'

            rack_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype_id=2).first()  # ID para rack
            sample.rack_name = rack_location.STORAGE_id_storage_1.storage_name if rack_location else 'No Asignado'

            box_location = sample.location_set.filter(
                STORAGE_TYPE_id_storagetype_id=1).first()  # ID para caja
            sample.box_name = box_location.STORAGE_id_storage_1.storage_name if box_location else 'No Asignado'

    return render(request, 'shipments_select.html', {'samples': samples})


@csrf_exempt
@require_POST
def update_samples_shipment(request):
    try:
        data = json.loads(request.body)
        sample_ids = data.get('sample_ids')  # Una lista de IDs de muestra

        if not sample_ids:
            return JsonResponse({'error': 'Faltan datos necesarios'}, status=400)

        # Obtener el último Shipment creado
        last_shipment = Shipment.objects.last()
        if not last_shipment:
            return JsonResponse({'error': 'No se encontró ningún envío'}, status=404)

        # Actualizar el SHIPMENT_id_shipment para cada muestra
        Sample.objects.filter(id_sample__in=sample_ids).update(
            SHIPMENT_id_shipment=last_shipment.id_shipment
        )

        return JsonResponse({'message': 'Envío actualizado con éxito'})

    except Sample.DoesNotExist:
        return JsonResponse({'error': 'Una o más muestras no encontradas'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)


def shipments_report(request):
    return render(request, 'shipments_report.html')


def samples_report(request):
    samples = Sample.objects.all().prefetch_related(
        Prefetch('location_set', queryset=Location.objects.select_related(
            'STORAGE_id_storage_1'))
    )

    if request.method == "GET":
        subject_id = request.GET.get('subject_id')
        sample_date = request.GET.get('sample_date')
        freezer_name = request.GET.get('freezer_number')
        rack_name = request.GET.get('rack_number')
        box_name = request.GET.get('box_number')

        if subject_id:
            samples = samples.filter(id_subject=subject_id)
        if sample_date:
            samples = samples.filter(date_sample=sample_date)

        # Filtros para freezer_name, rack_name, y box_name usando el modelo relacionado `Location` y luego `Storage`
        if freezer_name:
            samples = samples.filter(
                location__STORAGE_id_storage_1__storage_name=freezer_name,
                location__STORAGE_id_storage_1__STORAGE_TYPE_id_storagetype_id=3
            )
        if rack_name:
            samples = samples.filter(
                location__STORAGE_id_storage_1__storage_name=rack_name,
                location__STORAGE_id_storage_1__STORAGE_TYPE_id_storagetype_id=2
            )
        if box_name:
            samples = samples.filter(
                location__STORAGE_id_storage_1__storage_name=box_name,
                location__STORAGE_id_storage_1__STORAGE_TYPE_id_storagetype_id=1
            )

    # Agregando nombres de Freezer, Rack y Caja a cada sample
    for sample in samples:
        sample.freezer_name = sample.location_set.filter(
            STORAGE_TYPE_id_storagetype_id=3).first().STORAGE_id_storage_1.storage_name
        sample.rack_name = sample.location_set.filter(
            STORAGE_TYPE_id_storagetype_id=2).first().STORAGE_id_storage_1.storage_name
        sample.box_name = sample.location_set.filter(
            STORAGE_TYPE_id_storagetype_id=1).first().STORAGE_id_storage_1.storage_name

    context = {
        'samples': samples
    }

    return render(request, 'samples_report.html', context)
