"""
URL configuration for rideshare_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from users import views as user_views
from rideshare_backend.landing_view import landing_or_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),

    # Web Auth
    path('login/', user_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('signup/', user_views.signup_view, name='signup'),

    # Root: animated landing for guests, map dashboard for logged-in users
    path('', landing_or_dashboard, name='home'),

    # Protected web pages
    path('map/', login_required(TemplateView.as_view(template_name='index.html')), name='map'),
    path('search/', login_required(TemplateView.as_view(template_name='search.html')), name='search'),
    path('create-ride/', login_required(TemplateView.as_view(template_name='create_ride.html')), name='create_ride'),
    path('ride/<int:pk>/', login_required(TemplateView.as_view(template_name='ride_details.html')), name='ride_details'),
    path('chat/<int:pk>/', login_required(TemplateView.as_view(template_name='chat.html')), name='chat'),
    path('history/', login_required(TemplateView.as_view(template_name='history.html')), name='history'),
    path('ratings/', login_required(TemplateView.as_view(template_name='ratings.html')), name='ratings'),
    path('profile/', login_required(TemplateView.as_view(template_name='profile.html')), name='web_profile'),
    path('dashboard/', login_required(TemplateView.as_view(template_name='dashboard.html')), name='dashboard'),
    path('notifications/', login_required(TemplateView.as_view(template_name='notifications.html')), name='web_notifications'),

    # API Endpoints
    path('api/auth/', include('users.urls')),
    path('api/rides/', include('rides.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/sos/', include('sos.urls')),
]
