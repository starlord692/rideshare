from django.urls import path
from .views import SOSCreateView, SOSListView

urlpatterns = [
    path('trigger/', SOSCreateView.as_view(), name='sos-trigger'),
    path('history/', SOSListView.as_view(), name='sos-list'),
]
