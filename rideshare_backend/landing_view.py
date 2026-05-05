from django.shortcuts import render, redirect

def landing_or_dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'index.html') # This is the map dashboard
    return render(request, 'landing.html')
