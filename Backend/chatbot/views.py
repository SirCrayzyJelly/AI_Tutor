from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password = data['password']

        #Prikaz greške u slučaju istog username-a
        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username already exists'})

        User.objects.create_user(username=username, password=password)
        return JsonResponse({'status': 'success', 'message': 'User registered'})

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password = data['password']

        #prijava ako su podatci dobro uneseni
        user = authenticate(username=username, password=password)
        if user:
            return JsonResponse({'status': 'success', 'message': 'Login successful'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})

