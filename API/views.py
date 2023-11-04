from django.contrib.auth.models import User
from django.http import JsonResponse

from .models import Lead
from .serializers import LeadSerializer
from rest_framework import viewsets, permissions
from django.shortcuts import render
import json


# data Viewset


def send_json(request):
    data = [{'id': 1, 'name': 'Peter', 'email': 'peter@example.org', 'message': '123'},
            {'id': 2, 'name': 'Julia', 'email': 'julia@example.org', 'message': '321'}]


    return JsonResponse(data, safe=False)
