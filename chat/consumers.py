# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        try:
            print(text_data)
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            print(str(text_data_json) + "      " + self.room_group_name)
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': text_data_json['type'],
                    'message': message
                }
            )
        except:
            print("error in parsing message")

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message
        }))
    def roomTem(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message
        }))
    def nodeNewTem(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message
        }))
    def nodeTem(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message
        }))


    def graph(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message
        }))
    def minTemp(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message
        }))
    def maxTemp(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message
        }))
    def error(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message
        }))
    def pychart(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message
        }))
    def graph_config(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message
        }))

    def node_state(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message
        }))

    def nodeColor(self, event):
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message']
        }))

    def maxTemp(self, event):
        print("in MaxTemp")
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message']
        }))
    def minTemp(self, event):
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message']
        }))
    def send_notification(self, event):
        print("in notifications")
        self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['value']
        }))
