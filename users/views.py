import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, RegisterSerializer

logger = logging.getLogger(__name__)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class UserMeView(APIView):
    """Returns current authenticated user info for session-based browser requests."""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class CustomLoginView(LoginView):
    template_name = 'login.html'
    
    def form_valid(self, form):
        logger.info(f"Login success for user: {form.get_user().username}")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        username = form.data.get('username')
        logger.warning(f"Login failure for user: {username}")
        return super().form_invalid(form)

def signup_view(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        email = data.get('email', '')
        password = data.get('password')
        first_name = data.get('full_name', '') # From the new Full Name field
        phone_number = data.get('phone_number', '')
        role = data.get('role', 'passenger')
        ec_name = data.get('emergency_contact_name', '')
        ec_phone = data.get('emergency_contact_phone', '')

        if User.objects.filter(username=username).exists():
            logger.warning(f"Signup failed: Username {username} already exists")
            return render(request, 'signup.html', {'error': 'Username already exists'})
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                phone_number=phone_number,
                role=role,
                emergency_contact_name=ec_name,
                emergency_contact_phone=ec_phone
            )
            logger.info(f"Signup user created: {username} (ID: {user.id})")
            auth_login(request, user)
            return redirect('home')
        except Exception as e:
            logger.error(f"Error during signup for {username}: {str(e)}")
            return render(request, 'signup.html', {'error': 'An error occurred during signup'})
            
    return render(request, 'signup.html')
