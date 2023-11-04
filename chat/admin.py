from django.contrib import admin

from .models import Message, Notification, Node, State

admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(Node)
admin.site.register(State)