from django.urls import path
from .views import (
    RideListCreateView, RideRequestCreateView, RideDetailView,
    MyOfferedRidesView, MyRideRequestsView, RideRequestsForRideView,
    ApproveRideRequestView, RejectRideRequestView,
    CompleteRideView, CancelRideView
)

urlpatterns = [
    path('', RideListCreateView.as_view(), name='ride-list-create'),
    path('<int:pk>/', RideDetailView.as_view(), name='ride-detail'),
    path('<int:pk>/complete/', CompleteRideView.as_view(), name='complete-ride'),
    path('<int:pk>/cancel/', CancelRideView.as_view(), name='cancel-ride'),
    path('my-offered/', MyOfferedRidesView.as_view(), name='my-offered-rides'),
    path('my-requests/', MyRideRequestsView.as_view(), name='my-requests'),
    path('<int:pk>/requests/', RideRequestsForRideView.as_view(), name='ride-requests-list'),
    path('request/', RideRequestCreateView.as_view(), name='ride-request-create'),
    path('requests/<int:pk>/approve/', ApproveRideRequestView.as_view(), name='approve-request'),
    path('requests/<int:pk>/reject/', RejectRideRequestView.as_view(), name='reject-request'),
]
