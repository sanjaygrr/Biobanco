from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import IntegrityError
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Location
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
        # Get form data
        space_type = request.POST.get('space_type')
        space_value = request.POST.get('space_value')
        location_state = request.POST.get('location_state')
        description = request.POST.get('description')

        # Validate data
        if not all([space_type, space_value, location_state, description]):
            return render(request, 'create_space.html', {'error': 'All fields are required'})

        # Initialize all space values to 0
        box = cell = rack = freezer = 0

        # Assign the provided value to the selected space type
        if space_type == 'box':
            box = space_value
        elif space_type == 'cell':
            cell = space_value
        elif space_type == 'rack':
            rack = space_value
        elif space_type == 'freezer':
            freezer = space_value

        # Check if the space already exists
        space_exists = Location.objects.filter(
            box=box,
            cell=cell,
            rack=rack,
            freezer=freezer
        ).exists()

        if space_exists:
            messages.error(request, 'Este espacio ya existe')
        else:
            # Create and save the new location in the database
            new_location = Location(
                box=box,
                cell=cell,
                rack=rack,
                freezer=freezer,
                location_state=location_state,
                description=description
            )
            new_location.save()

            messages.success(request, 'Location registered successfully!')
            return redirect('create_space')

    return render(request, 'create_space.html')


def space_list(request):
    locations = Location.objects.all()

    number_query = request.GET.get('number')
    type_query = request.GET.get('type')
    status_query = request.GET.get('status')

    # Intenta convertir number_query a int si está presente, si no, déjalo como None
    try:
        number_query = int(number_query) if number_query else None
    except ValueError:
        number_query = None

    # Filtrado por tipo y número
    if type_query and number_query is not None:
        locations = locations.filter(**{f"{type_query}": number_query})

    # Filtrado solo por tipo
    elif type_query:
        locations = locations.filter(**{f"{type_query}__gt": 0})

    # Filtrado solo por número
    elif number_query is not None:
        locations = locations.filter(
            Q(box=number_query) |
            Q(freezer=number_query) |
            Q(rack=number_query) |
            Q(cell=number_query)
        )

    # Filtrado por estado
    if status_query:
        if status_query == 'enabled':
            locations = locations.filter(location_state=True)
        elif status_query == 'disabled':
            locations = locations.filter(location_state=False)

    return render(request, 'space_list.html', {'spaces': locations})


@csrf_exempt
@require_POST
def update_space_status(request, space_id):
    try:
        location = Location.objects.get(pk=space_id)
        new_status = request.POST.get('location_state')

        if new_status not in ['0', '1']:
            return JsonResponse({'error': 'Invalid status'}, status=400)

        location.location_state = new_status
        location.save()

        return JsonResponse({'message': 'Status updated successfully'})
    except Location.DoesNotExist:
        return JsonResponse({'error': 'Location not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def create_sample(request):
    return render(request, 'create_sample.html')


def sample_list(request):
    return render(request, 'sample_list.html')


def trazability(request):
    return render(request, 'trazability.html')
