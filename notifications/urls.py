from django.urls import path
from .views import NotificationListView, NotificationReadView, UnreadCountView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', NotificationReadView.as_view(), name='notification-read'),
    path('unread-count/', UnreadCountView.as_view(), name='unread-count'),
]
