from django.urls import path
from .views import MessageListView

urlpatterns = [
    path('<int:ride_id>/', MessageListView.as_view(), name='message-list'),
]
