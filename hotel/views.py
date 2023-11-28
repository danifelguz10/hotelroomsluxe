from django.shortcuts import render
from django.views import View
# Create your views here.
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UserLoginForm, UserSignUpForm, RoomForm, RoomFormEdit, ReservationForm, UpdateReservationStatusForm
from .models import UserProfile, Room, Reservation

def home(request):
    rooms = Room.objects.all()
    return render(request, 'views/index.html', {'rooms': rooms})

def index(request):
    loginForms = UserLoginForm()
    return render(request, 'views/auth/login.html', {'loginForms' : loginForms })
def signupview(request):
    signupForms = UserSignUpForm()
    return render(request, 'views/auth/register.html', {'signupForms' : signupForms })

def login_view(request):
    if request.method == 'POST':
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                # El usuario ha sido autenticado, puedes redirigirlo a una página de bienvenida
                return redirect('hotel:home')  # Cambia 'welcome_view' por la URL de tu página de bienvenida
    else:
        loginForms = UserLoginForm()

    loginForms = UserLoginForm()
    messages.error(request, 'Credenciales Invalidas')
    return render(request, 'views/auth/login.html', {'loginForms': loginForms})



def signup(request):
    signup_form = UserSignUpForm(request.POST or None)
    if signup_form.is_valid():
        email = signup_form.cleaned_data.get('email')
        first_name = signup_form.cleaned_data.get('first_name')
        document_number = signup_form.cleaned_data.get('document_number')
        last_name = signup_form.cleaned_data.get('last_name')
        password = signup_form.cleaned_data.get('password')
        try:
            user = get_user_model().objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                document_number=document_number,
                password=make_password(password),
                is_active=True
            )
            login(request, user)
            return redirect('hotel:home')

        except Exception as e:
            print(e)
            return JsonResponse({'detail': f'{e}'})

    messages.error(request, 'Las Contrasenas no coinciden')
    return redirect('hotel:index')

def logout_view(request):
    logout(request)
    return redirect('hotel:index')


@login_required(login_url='index')
def profile_view(request):
    return render(request, 'user/profile.html')


def user_detail(request, slug):
    user_detail = get_object_or_404(get_user_model(), slug=slug)
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes Iniciar sesion para mas funcionalidades')

    return render(request, 'user/user_detail.html', {'user_detail': user_detail})


def room_list(request):
    areas = Room.objects.all()
    forms = RoomForm()
    product_forms = [(room, RoomFormEdit(instance=room)) for room in areas]
    return render(request, 'views/parameters/room/room_list.html', {'product_forms': product_forms, 'forms': forms})

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    return render(request, 'views/room/room_detail.html', {'room': room})

def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habitación creada exitosamente.')
            return redirect('hotel:roomlist')
        else:
            messages.error(request, 'Hubo un error al crear la habitación. Verifica los datos ingresados.')
    return redirect('hotel:roomlist')

def room_update(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomFormEdit(request.POST, request.FILES, instance=room)
        if form.is_valid():
            # Guardar la imagen actual en el nuevo campo
            form.current_image = room.image
            form.save()

            messages.success(request, 'Habitación actualizada exitosamente.')
            return redirect('hotel:roomlist')
        else:
            messages.error(request, 'Hubo un error al actualizar la habitación. Verifica los datos ingresados.')
    return redirect('hotel:roomlist')

def room_delete(request, pk):
    product = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        product.delete()
    
    return redirect('hotel:roomlist')  # Redirigir a la lista de productos

def reservation_list(request):
    reservations = Reservation.objects.all()
    return render(request, 'views/reservations/reservationlist.html', {'reservations': reservations})

def reservation_create(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            check_in_date = form.cleaned_data['check_in_date']
            check_out_date = form.cleaned_data['check_out_date']

            # Crear la reserva
            reservation = Reservation.objects.create(
                room=room,
                user=request.user,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
            )


            messages.success(request, 'Habitación reservada exitosamente.')
            return redirect('hotel:home')
        
    messages.error(request, 'No se puede reservar una Habitacion antes de la fecha actual')
    return redirect('hotel:home')

def reservation_update(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)

    if request.method == 'POST':
        form = UpdateReservationStatusForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()

            # Obtener el nuevo estado desde la solicitud POST
            nuevo_estado = request.POST.get('status')

            # Actualizar el estado de la habitación
            habitacion = reservation.room
            habitacion.state = 'Ocupado' if nuevo_estado == 'Aprobada' else 'Disponible'
            habitacion.save()

            return redirect('hotel:reservationlist')

    return render(request, 'update_reservation_status.html', {'form': form, 'reservation': reservation})

def reservation_delete(request, pk):
    try:
        reserva = Reservation.objects.get(pk=pk)
        reserva.delete()
        return redirect('hotel:reservationlist')    
    except Reservation.DoesNotExist:
        return JsonResponse({'error': 'La reserva no existe'}, status=404)
    
def reservation_user(request):
    user = request.user

    # Filtrar las reservas del usuario actual
    reservations = Reservation.objects.filter(user=user)

    # Renderizar la plantilla con las reservas filtradas
    return render(request, 'views/reservations/reservationuser.html', {'reservations': reservations})
    
def reservation_cancel(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    # Lógica para la cancelación de la reserva, similar a tu lógica existente
    if request.method == 'POST':
        if reservation.status == 'Aprobada':
            habitacion = reservation.room
            habitacion.state = 'Disponible'
            habitacion.save()
            
        # Procesar la cancelación de la reserva
        reservation.status = 'Cancelada'
        reservation.save()
        
        # Actualizar el estado de la habitación
        
    
    return redirect('hotel:reservationuser')

