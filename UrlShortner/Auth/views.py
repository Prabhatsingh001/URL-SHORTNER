from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, "home.html")


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")


def profile(request):
    return render(request, "profile.html")


def forgot_password(request):
    return render(request, "forgot_password.html")
