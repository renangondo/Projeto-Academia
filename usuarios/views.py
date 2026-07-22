from django.shortcuts import render

# Create your views here.
from django.contrib.auth import logout
from django.shortcuts import redirect


def LogoutView(request):
    logout(request)
    return redirect('login')