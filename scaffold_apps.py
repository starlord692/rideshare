import os
os.makedirs('notifications', exist_ok=True)
with open('notifications/__init__.py', 'w') as f: f.write('')

with open('notifications/apps.py', 'w') as f:
    f.write('''from django.apps import AppConfig\n\nclass NotificationsConfig(AppConfig):\n    default_auto_field = "django.db.models.BigAutoField"\n    name = "notifications"\n''')

with open('notifications/models.py', 'w') as f: f.write('from django.db import models\n')
with open('notifications/views.py', 'w') as f: f.write('from rest_framework import views\n')
with open('notifications/urls.py', 'w') as f: f.write('from django.urls import path\nurlpatterns = []\n')

os.makedirs('sos', exist_ok=True)
with open('sos/__init__.py', 'w') as f: f.write('')

with open('sos/apps.py', 'w') as f:
    f.write('''from django.apps import AppConfig\n\nclass SosConfig(AppConfig):\n    default_auto_field = "django.db.models.BigAutoField"\n    name = "sos"\n''')

with open('sos/models.py', 'w') as f:
    f.write('''from django.db import models\nfrom django.conf import settings\nfrom rides.models import Ride\n\nclass EmergencyAlert(models.Model):\n    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)\n    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)\n    lat = models.FloatField()\n    lng = models.FloatField()\n    timestamp = models.DateTimeField(auto_now_add=True)\n''')
with open('sos/views.py', 'w') as f:
    f.write('''from rest_framework import generics, permissions\nfrom .models import EmergencyAlert\nfrom rest_framework import serializers\nclass EmergencySerializer(serializers.ModelSerializer):\n    class Meta:\n        model = EmergencyAlert\n        fields = "__all__"\nclass SOSCreateView(generics.CreateAPIView):\n    serializer_class = EmergencySerializer\n    permission_classes = [permissions.IsAuthenticated]\n    def perform_create(self, serializer):\n        serializer.save(user=self.request.user)\n''')
with open('sos/urls.py', 'w') as f:
    f.write('''from django.urls import path\nfrom .views import SOSCreateView\nurlpatterns = [\n    path("alert/", SOSCreateView.as_view(), name="sos-alert"),\n]\n''')
