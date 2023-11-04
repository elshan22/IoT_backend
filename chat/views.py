# chat/views.py
from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# from .serializers import GraphSetting
# from .models import CartItem
from .serializers import GraphSetting, NodeState


def index(request):
    return render(request, 'chat/index.html', {})


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })


class RecieveDataGraph(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(request.data)
        serializer = GraphSetting(data=request.data)
        if serializer.is_valid():
            print("data validated")
            serializer.save()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)


class RecieveDataState(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(request.data)
        serializer = NodeState(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)