from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views.generic import ListView, FormView, View, DeleteView, UpdateView
from django.urls import reverse, reverse_lazy
from .models import Room, Booking
from .forms import AvailabilityForm
from hotel.booking_functions.availability import check_availability
from hotel.booking_functions.get_room_cat_url_list import get_room_cat_url_list
from django import forms

# Create your views here.

class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index_as_view.html')
        
def RoomListView(request):
    room_category_url_list = get_room_cat_url_list()
    context={
        "room_list": room_category_url_list,
    }
    return render(request, 'room_list_view.html', context)

class BookingListView(ListView):
    model = Booking
    template_name="booking_list_view.html"
    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_staff:
            booking_list = Booking.objects.all()
            return booking_list
        else:
            booking_list = Booking.objects.filter(user=self.request.user)
            return booking_list
    
def user_bookings(request):
    user = request.user
    bookings = Booking.objects.filter(user=user)
    rooms = [booking.room for booking in bookings]
    return render(request, 'user_bookings.html', {'rooms': rooms})
    
class RoomDetailView(View):
    def get(self, request, *args, **kwargs):
        category = self.kwargs.get('category', None)
        form = AvailabilityForm()
        room_list = Room.objects.filter(category=category)

        if len(room_list) > 0:
            room = room_list[0]
            room_category = dict(room.ROOM_CATEGORIES).get(room.category, None)
            context = {
                'room_category': room_category,
                'form': form,
            }
            return render(request, 'room_detail_view.html', context)
        else:
            return HttpResponse('Category does not exist')

    def post(self, request, *args, **kwargs):
        category = self.kwargs.get('category', None)
        room_list = Room.objects.filter(category=category)
        form = AvailabilityForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

        available_rooms = []
        for room in room_list:
            if check_availability(room, data['check_in'], data['check_out']):
                available_rooms.append(room)

        if len(available_rooms) > 0:
            room = available_rooms[0]
            booking = Booking.objects.create(
                user=self.request.user,
                room=room,
                check_in=data['check_in'],
                check_out=data['check_out']
            )
            booking.save()
            return HttpResponse(booking)
        else:
            return HttpResponse('All of this category of rooms are booked!! Try another one')


class BookingView(FormView):
    form_class = AvailabilityForm
    template_name = 'availability_form.html'

    def form_valid(self, form):
        data = form.cleaned_data
        room_list = Room.objects.filter(category=data['room_category'])
        available_rooms = []
        for room in room_list:
            if check_availability(room, data['check_in'], data['check_out']):
                available_rooms.append(room)

        if len(available_rooms) > 0:
            room = available_rooms[0]
            booking = Booking.objects.create(
                user=self.request.user,
                room=room,
                check_in=data['check_in'],
                check_out=data['check_out']
            )
            booking.save()
            return HttpResponse(booking)
        else:
            return HttpResponse('All of this category of rooms are booked!! Try another one')
            
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'check_in', 'check_out']
            
class UpdateBookingView(UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'update_booking_view.html'
    success_url = reverse_lazy('hotel:BookingListView')

    def form_valid(self, form):
        booking = form.save(commit=False)
        room = booking.room
        check_in = booking.check_in
        check_out = booking.check_out
        booked_rooms = Booking.objects.exclude(pk=booking.pk).filter(room=room, check_in__lte=check_out, check_out__gte=check_in)
        if booked_rooms:
            unavailable_dates = [f"{b.check_in.strftime('%Y-%m-%d')} to {b.check_out.strftime('%Y-%m-%d')}" for b in booked_rooms]
            form.add_error('room', f"The room is not available for the selected dates. Already booked for {', '.join(unavailable_dates)}")
            return super().form_invalid(form)
        booking.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('hotel:BookingDetailView', kwargs={'pk': self.object.pk})


            
class CancelBookingView(DeleteView):
    model = Booking
    template_name = 'booking_cancel_view.html'
    success_url = reverse_lazy('hotel:BookingListView')