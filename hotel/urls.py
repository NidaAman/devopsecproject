from django.urls import path
from .views import Index, RoomListView, BookingListView, BookingView, RoomDetailView, CancelBookingView, UpdateBookingView

app_name = 'hotel'

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('room_list/', RoomListView, name='RoomListView'),
    path('booking_list/', BookingListView.as_view(), name='BookingListView'),
    path('room/<category>', RoomDetailView.as_view(), name='RoomDetailView'),
    path('booking/cancel/<pk>', CancelBookingView.as_view(), name='CancelBookingView'),
    path('booking/update/<pk>', UpdateBookingView.as_view(), name='UpdateBookingView')

]