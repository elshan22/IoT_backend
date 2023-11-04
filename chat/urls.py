# chat/urls.py
from django.urls import path

from . import views
from .views import RecieveDataGraph, RecieveDataState

app_name = 'chat'
urlpatterns = [
    path('', views.index, name='index'),
    path('graphSetting/', RecieveDataGraph.as_view(), name='graphSetting'),
    path('nodeState/', RecieveDataState.as_view(), name='state node'),
    path('<str:room_name>/', views.room, name='room'),
]