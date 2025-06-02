from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

