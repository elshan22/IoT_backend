import json

from django.contrib.auth import get_user_model
from django.db import models

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

User = get_user_model()


class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username

    def last_10_messages(self):
        return Message.objects.order_by('-timestamp').all()[:10]


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.TextField(max_length=100)
    is_seen = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        notification_objs = Notification.objects.filter(is_seen=False).count()
        data = {'count': notification_objs, 'current_notification': self.notification}
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'not_message',
                'message': json.dumps(data)
            }
        )

        super(Notification, self).save(*args, **kwargs)


class Node(models.Model):
    id = models.IntegerField(primary_key=True)
    setT = models.CharField(null=True,blank=True, max_length=200)
    node_state = models.CharField(null=True,blank=True,max_length=200)
    fanCoilTem = models.CharField(null=True,blank=True,max_length=200)
    homeTem = models.CharField(null=True,blank=True,max_length=200)
    Time = models.CharField(null=True,blank=True,max_length=200,default="none")
    neighbors = models.CharField(null=True,blank=True,max_length=400)

    def save(self, *args, **kwargs):
        super(Node, self).save(*args, **kwargs)
        channel_layer = get_channel_layer()
        node_objs = list(Node.objects.all().values("id", "neighbors","node_state"))
        data = json.dumps(node_objs)
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'graph_config',
                'message': json.dumps(data)
            }
        )

    def __str__(self):
        return str(self.id)

class State(models.Model):
    id = models.AutoField(primary_key=True)
    Node = models.ForeignKey(Node,null=True,blank=True, on_delete=models.CASCADE)
    DateTime = models.CharField(null=True,blank=True,max_length=200)
    temperature = models.CharField(null=True,blank=True,max_length=200)

    def save(self, *args, **kwargs):
        super(State, self).save(*args, **kwargs)
        channel_layer = get_channel_layer()
        state_objs = list(State.objects.all().values("DateTime", "temperature","Node__id"))
        # state_objs.append(a)
        data = json.dumps(state_objs)
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'node_state',
                'message': json.dumps(data)
            }
        )

    def __str__(self):
        return str(self.id)