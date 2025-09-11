from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Hotel, Room, Booking
from .forms import BookingForm
from datetime import datetime

def home(request):
    hotels = Hotel.objects.all()
    return render(request, 'hotel/home.html', {'hotels': hotels})

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    return render(request, 'hotel/hotel_detail.html', {'hotel': hotel})

def search(request):
    location = request.GET.get('location', '')
    check_in = request.GET.get('check_in', '')
    check_out = request.GET.get('check_out', '')
    
    hotels = Hotel.objects.all()
    
    if location:
        hotels = hotels.filter(location__icontains=location)
    
    context = {
        'hotels': hotels,
        'location': location,
        'check_in': check_in,
        'check_out': check_out
    }
    
    return render(request, 'hotel/search.html', context)

@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room = room
            
            # Check if room is available
            conflicting_bookings = Booking.objects.filter(
                room=room,
                check_in_date__lt=booking.check_out_date,
                check_out_date__gt=booking.check_in_date,
                is_cancelled=False
            )
            
            if conflicting_bookings.exists():
                messages.error(request, 'This room is not available for the selected dates.')
            else:
                booking.save()
                messages.success(request, 'Booking successful!')
                return redirect('my_bookings')
    else:
        # Pre-fill dates from search if available
        check_in = request.GET.get('check_in', '')
        check_out = request.GET.get('check_out', '')
        
        initial_data = {}
        if check_in:
            initial_data['check_in_date'] = datetime.strptime(check_in, '%Y-%m-%d').date()
        if check_out:
            initial_data['check_out_date'] = datetime.strptime(check_out, '%Y-%m-%d').date()
            
        form = BookingForm(initial=initial_data)
    
    return render(request, 'hotel/book_room.html', {'form': form, 'room': room})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'hotel/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        booking.is_cancelled = True
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('my_bookings')
    
    return render(request, 'hotel/cancel_booking.html', {'booking': booking})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'hotel/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'hotel/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')