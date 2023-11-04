import copy
from math import factorial
from sqlite3 import Date
from warnings import catch_warnings
from django.contrib.auth.views import LogoutView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework import status, authentication, generics, permissions
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, Node, NodeStation, Neighbor, Allocation, UserNode, Security, SecurityStation, FanCoil, \
    Floor, MatFile
import json
from django.contrib.auth import get_user_model
from django.db import models
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import paho.mqtt.client as mqtt
from .serializers import CustomUserSerializer, LogoutSerializer, Floorserializer, MatFileserializer
import logging
import threading
import time
from django.utils import timezone
from datetime import datetime
import requests
from tokenize import Name
from unicodedata import category
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import datetime
import os

# from SCPS import settings

User = get_user_model()

# Create your views here.
client = mqtt.Client()

# redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
#                                   port=settings.REDIS_PORT, db=0)

def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if (gm > 2):
        gy2 = gy + 1
    else:
        gy2 = gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if (days > 365):
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if (days < 186):
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return [jy, jm, jd]


def jalali_to_gregorian(jy, jm, jd):
    jy += 1595
    days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
    if jm < 7:
        days += (jm - 1) * 31
    else:
        days += ((jm - 7) * 30) + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += ((days - 1) // 365)
        days = (days - 1) % 365
    gd = days + 1
    if ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
        kab = 29
    else:
        kab = 28
    sal_a = [0, 31, kab, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    while (gm < 13 and gd > sal_a[gm]):
        gd -= sal_a[gm]
        gm += 1
    return [gy, gm, gd]


def Graphws(z):
    nodes = []
    links = []
    for t in z["graph"]:
        p = {
            'id': str(t["id"])
        }
        nodes.append(p)
        for n in t["neighbor"]:
            o = {
                'source': str(t["id"]),
                'target': str(n["id"])
            }
            links.append(o)
    data = {'graph': nodes, 'links': links}
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        'chat_test',  # group _ name
        {
            'type': 'graph',
            'message': json.dumps(data)
        }
    )


def errorws(z):
    for t in z["errors"]:
        data = {'node': str(t["id"]), 'color': 'red', 'message': 'Error Code :' + str(t["code"])}
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'error',
                'message': json.dumps(data)
            }
        )


def pychart(z):
    l = 0
    w = 0
    p = 0
    for i in z["data"]:
        l = l + 1
    # for i in z["errors"]:
    #    w = w + 1
    for i in Node.objects.all():
        p = p + 1
    active = ((l - w) / p) * 100
    deactive = (w / p) * 100
    onhold = ((p - l) / p) * 100
    mymessage = []
    l = {'name': 'Group A', 'value': active}
    mymessage.append(l)
    l = {'name': 'Group B', 'value': deactive}
    mymessage.append(l)
    l = {'name': 'Group C', 'value': onhold}
    mymessage.append(l)
    data = mymessage
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_test',  # group _ name
        {
            'type': 'pychart',
            'message': json.dumps(data)
        }
    )


def roomTem(z):
    sum = 0
    counter = 0
    min = 196
    max = 0
    for t in z["data"]:
        sum = sum + float(t["homeT"])
        counter = counter + 1
        if t["homeT"] > max:
            max = t["homeT"]
        if t["homeT"] < min:
            min = t["homeT"]
    Avg = sum / counter
    data = {'date': str(timezone.now()), 'tem': Avg}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_test',  # group _ name
        {
            'type': 'roomTem',
            'message': json.dumps(data)
        }
    )


def minandmax(z):
    sum = 0
    counter = 0
    min = 10000000
    max = 0
    np = NodeStation.objects.all()
    xl = np.count()
    o = 0
    for t in np:
        o = o + 1
        if o < xl - 5:
            continue
        sum = sum + t.HomeTemperature
        counter = counter + 1
        if t.HomeTemperature > max:
            max = t.HomeTemperature
            maxid = t.Node.id
        if t.HomeTemperature < min:
            min = t.HomeTemperature
            minid = t.Node.id
    Avg = sum / counter
    data = {'id': maxid, 'temp': str(max)}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_test',  # group _ name
        {
            'type': 'maxTemp',
            'message': data
        }
    )
    data = {'id': minid, 'temp': str(min)}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_test',  # group _ name
        {
            'type': 'minTemp',
            'message': data
        }
    )


def nodeNewTem(Data):
    for RecieveData in Data["data"]:
        mode = ""
        if RecieveData["workmode"] == 0:
            mode = "Sleep"
        if RecieveData["workmode"] == 1:
            mode = "EnergySaving"
        if RecieveData["workmode"] == 2:
            mode = "Maintenance"
        if RecieveData["workmode"] == 3:
            mode = "Maintenance"
        if RecieveData["workmode"] == 4:
            mode = "Classic"

        l = Node.objects.get(MacAddress=RecieveData['id']).id
        p = Node.objects.get(MacAddress=RecieveData['id'])
        zp = Security.objects.all()[0].Name
        fanState1 = ""
        fanState2 = ""
        valveState1 = ""
        valveState2 = ""
        if RecieveData["fanState"][0] == 1:
            fanState1 = "on"
        else:
            fanState1 = "off"
        try:
            if RecieveData["fanState"][1] == 1:
                fanState2 = "on"
            else:
                fanState2 = "off"
        except:
            u = 0
        if RecieveData["valveState"][0] == 1:
            valveState1 = "on"
        else:
            valveState1 = "off"
        try:
            if RecieveData["valveState"][1] == 1:
                valveState2 = "on"
            else:
                valveState2 = "off"
        except:
            u = 0
        light = ""
        humidity = ""
        analog1 = ""
        analog2 = ""
        print(RecieveData["light"])
        if RecieveData["light"] == -1 or RecieveData["light"] == 65535 or RecieveData['light'] is None:
            light = "Null"
        else:
            light = str(int(RecieveData["light"] * 100) / 100)
        if RecieveData["humidity"] == 255:
            humidity = "Null"
        else:
            humidity = str(int(RecieveData["humidity"] * 100) / 100)
        if RecieveData["analogSensors"][0] == 65535:
            analog1 = "Null"
        else:
            analog1 = str(RecieveData["analogSensors"][0])
        if RecieveData["analogSensors"][1] == 65535:
            analog2 = "Null"
        else:
            analog2 = str(RecieveData["analogSensors"][1])
        print(light)

        j = int(RecieveData["homeT"] * 100) / 100
        data = {'nodeId': str(l), 'time': str(timezone.now()), 'temp': j,
                "lastOccupancy": str(p.LastTime),
                "lightSensor": light,
                "humiditySensor": humidity,
                "analogSensor1": analog1,
                "analogSensor2": analog2,
                "fanAir1": fanState1,
                "fanAir2": fanState2,
                "hvac1": valveState1,
                "hvac2": valveState2,
                "parameter": RecieveData["numFCU"],
                "mode": mode,
                "setPoint": RecieveData["setT"],
                "fanAir1Temp": str(int(RecieveData["fancoilT"][0] * 100) / 100)
                }
    channel_layer = get_channel_layer()
    if zp == str(l):
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'nodeNewTem',
                'message': data
            }
        )
    np = NodeStation.objects.all()
    xl = np.count()
    o = 0
    xk = Node.objects.all().count()
    data = []
    for RecieveData in np:
        o = o + 1
        if o < xl - xk + 1:
            continue
        if RecieveData.HomeTemperature + 2 < RecieveData.SetPointTemperature:
            data.append([str(RecieveData.Node.id), "#0000ff"])
            # data = [[str(l), "#0000ff"],["0", "#ffc0cb"]]
        elif RecieveData.HomeTemperature + 2 < RecieveData.SetPointTemperature:
            data.append([str(RecieveData.Node.id), "#ff0000"])
            # data = [[str(l), "#ff0000"],["0", "#ffc0cb"]]
        else:
            data.append([str(RecieveData.Node.id), "#00ff00"])
            # data = [[str(l), "#00ff00"],["0", "#ffc0cb"]]
    data.append(["0", "#ffc0cb"])
    async_to_sync(channel_layer.group_send)(
        'chat_test',  # group _ name
        {
            'type': 'nodeColor',
            'message': data
        }
    )


def ReciveMqtt1(z):
    for t in z["graph"]:
        k = Node()
        k.MacAddress = t["id"]
        print(Node.objects.filter(MacAddress=t["id"]).count())
        if Node.objects.filter(MacAddress=t["id"]).count() == 0:
            k.save()
    Neighbor.objects.all().delete()
    for t in z["graph"]:
        nodeid1 = t["id"]
        for n in t["neighbor"]:
            nodeid2 = n["id"]
            rssi = n["rssi"]
            h = Neighbor()
            node1 = Node.objects.get(MacAddress=nodeid1)
            node2 = Node.objects.get(MacAddress=nodeid2)
            h.Node1 = node1
            h.Node2 = node2
            h.RSSI = rssi
            h.save()
            # o = t["nums"]
            # u = 0
            # if Node.objects.filter(MacAddress=nodeid1).count() > o:
            #    o = Node.objects.filter(MacAddress=nodeid1).count() - o
            # while u < o:
            #    l = FanCoil()
            #    l.Node = Node.objects.get(MacAddress=nodeid1)
            #    u = u + 1
            #    l.save()

    Graphws(z)


def ReciveMqtt2(Data):
    timeZone = timezone.now()
    dateTimeNow = datetime(timeZone.year, timeZone.month, timeZone.day, timeZone.hour, timeZone.minute, timeZone.second,
                           0)

    global Dungle_data
    print(Data)
    if Data['data'][0]['id'] == '1c:9d:c2:4a:d4:b4':
        Dungle_data = Data
    for recieveData in Data["data"]:
        nodes = NodeStation()
        nodeid = recieveData["id"]

        try:
            node = Node.objects.get(MacAddress=nodeid)
        except:
            node = Node()
            node.MacAddress = recieveData["id"]
            node.save()

        nodes.Node = node
        s = 0
        l = 0

        # check number of parameter sent by the gateway
        if (len(recieveData["fancoilT"]) != 2):
            if len(recieveData["fancoilT"]) == 1:
                recieveData['fancoilT'].append(0)
            else:  # means if 0
                recieveData['fancoilT'] = [0, 0]

        if (len(recieveData["fanState"]) != 2):
            if len(recieveData["fanState"]) == 1:
                recieveData['fanState'].append(0)
            else:  # means if 0
                recieveData['fanState'] = [0, 0]

        nodes.FanCoilTemperature = int(((recieveData["fancoilT"][0] + recieveData["fancoilT"][0]) / 2) * 100) / 100
        nodes.HomeTemperature = int(recieveData["homeT"] * 100) / 100
        nodes.Presence = recieveData["present"]
        nodes.FanCoil1 = int(recieveData["fancoilT"][0] * 100) / 100

        nodes.FanCoil2 = int(recieveData["fancoilT"][1] * 100) / 100

        nodes.humidity = recieveData["humidity"]
        nodes.valveState1 = recieveData["valveState"][0]
        # nodes.valveState2=t["valveState"][1]
        nodes.analog1 = recieveData["analogSensors"][0]
        nodes.analog2 = recieveData["analogSensors"][1]
        try:
            nodes.light = int(recieveData["light"] * 100) / 100
        except:
            nodes.light = 0

        if recieveData["present"] < 5:
            nodes.LastTime = dateTimeNow
            node.LastTime = dateTimeNow
        else:
            nodes.LastTime = node.LastTime

        if (recieveData["fanState"][0]) and recieveData["fanState"][0] == 1:
            nodes.fanState1 = True
        else:
            nodes.fanState1 = False
        # if t["fanState"][1]==1:
        #    nodes.fanState2=True
        # else :
        #    nodes.fanState2=False
        if recieveData["valveState"][0] == 1:
            nodes.valveState1 = True
        else:
            nodes.valveState1 = False
        # if t["valveState"][1]==1:
        #    nodes.valveState2=True
        # else :
        #    nodes.valveState2=False

        # nodes.faucetState=t["faucetState"]
        nodes.SetPointTemperature = recieveData["setT"]
        nodes.DateTime = dateTimeNow
        nodes.save()
        node.save()
    # for t in z["errors"]:
    #     node2 = Node.objects.get(MacAddress=t["id"])
    #     node2.ErrorId = t["code"]
    #     node2.save()
    # errorws(z)
    # for t in z["security"]:
    #    Securitys=SecurityStation()
    #   Securitys.Name=t["name"]
    #  Securitys.Value=t["value"]
    # Securitys.save()
    minandmax(Data)
    pychart(Data)
    roomTem(Data)
    nodeNewTem(Data)


def on_connect(client, userdata, flags, rc):
    print("Connected to broker!")
    client.subscribe("scps/client/1")


def on_message(client, userdata, message):
    l = message.payload.decode()
    # print(message.payload.decode())
    z = json.loads(l)
    if z["type"] == "01":
        ReciveMqtt1(z)
    if z["type"] == "02":
        ReciveMqtt2(z)


def MqttRun():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('91.98.15.243', 1700)
    client.subscribe("scps/client/2")
    client.loop_start() #this works

MqttRun()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user: CustomUser):
        token = super().get_token(user)

        token['role'] = user.role
        token['email'] = user.email
        token['password'] = user.password
        token['user_id'] = user.id
        token['user_name'] = user.user_name
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomUserCreate(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format='json'):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlacklistTokenUpdateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(generics.GenericAPIView):
    print("in logout")
    serializer_class = LogoutSerializer

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class sendDungleData(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # TODO
        dry = Dungle_data['data'][0]['homeT']
        wet = Dungle_data['data'][0]['fancoilT'][0]
        data = {'dry_temp': dry,
                'wet_temp': wet}
        return Response(data=data, status=status.HTTP_200_OK)


class sendLastData(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # TODO
        l = NodeStation.objects.all().order_by("DateTime")
        sum = 0
        d = datetime.now()
        counter = 1
        en = 0
        p = []
        for i in l:
            if d == i.DateTime:
                sum = sum + i.HomeTemperature
                # print('sum : ' + str(sum))
                counter = counter + 1
                # print('counter : ' + str(counter))
            else:
                if en == 0:
                    d = i.DateTime
                    counter = 1
                    sum = i.HomeTemperature
                    en = 1
                    continue
                Avg = sum / counter
                l = {'date': str(d), 'tem': int(int(Avg * 100) / 100)}
                p.append(l)
                channel_layer = get_channel_layer()
                d = i.DateTime
                counter = 1
                sum = i.HomeTemperature
        data = p
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'roomTem',
                'message': json.dumps(data)
            }
        )
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        # TODO
        NodeArray = Node.objects.all()
        # print(str(NodeArray))
        for i in NodeArray:
            # print(request.data["nodeid"])
            if str(i.id) == str(request.data["nodeid"]):
                l = Security.objects.all()[0]
                l.Name = str(i.id)
                l.save()
                NodeStationArray = NodeStation.objects.filter(Node=i)
                g = NodeStationArray.count()
                print(g)
                times = []
                temps = []
                # print(request.data["nodeid"])
                for z in NodeStationArray:
                    if (z.id > g - 500):
                        times.append(str(z.DateTime))
                        temps.append(str(z.HomeTemperature))
                data = {'nodeid': str(i.id), 'times': times, 'temps': temps}
        return Response(data=data, status=status.HTTP_200_OK)


class SetConfigNode(APIView):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request = {}

    def change_valves(self):
        request = self.request
        a = 0
        b = 0
        c = -1
        # valve_cammand = []
        print(request)
        dictsend = {}
        # MyNode = Node.objects.get(MacAddress=request.data["nodeid"])
        # MyNode.SetPointTemperature = request.data["temp"]
        if request.data["perm"] == "YES":
            # MyNode.ControlStatus = True
            b = 1
        elif request.data["perm"] == "NO":
            # MyNode.ControlStatus = False
            b = 0
        if request.data["sleepMode"] == True:
            # MyNode.mode = "sleepMode"
            # MyNode.status = False
            c = 0
            a = 0
        if request.data["energysavingMode"] == True:
            # MyNode.mode = "optimalMode"
            c = 1
        if request.data["manualMode"] == True:
            # MyNode.mode = "manualMode"
            c = 2
        if request.data["classicMode"] == True:
            # MyNode.mode = "manualMode"
            c = 4

        #    NodeArray = Node.objects.all()
        #    print(str(NodeArray))
        #    for i in NodeArray:
        #        if i.MacAddress == request.data["nodeid"]:
        #            NodeStationArray = FanCoil.objects.filter(Node=i)
        #            o = 1
        #            for z in NodeStationArray:
        #                if o > 3:
        #                    o = 3
        #                valve_cammand.append(request.data["cValve" + str(o)])
        #                z.valv = request.data["cValve" + str(o)]
        #                o = o + 1
        #                z.save()
        #    MyNode.save()
        valve_cammand = []
        fan_command = []
        # valve_cammand.append(float('inf') if request.data['cvalve1'] else request.data['cvalve1'])
        # valve_cammand.append(float('inf') if request.data['cvalve2'] else request.data['cvalve2'])
        # fan_command.append(float('inf') if request.data['fanAir1'] else request.data['fanAir1'])
        # fan_command.append(float('inf') if request.data['fanAir2'] else request.data['fanAir2'])
        #
        if request.data["cValve1"] == True:
            valve_cammand.append(1)
        else:
            valve_cammand.append(0)
        if request.data["cValve2"] == True:
            valve_cammand.append(1)
        else:
            valve_cammand.append(0)
        if request.data["fanAir1"] == True:
            fan_command.append(1)
        else:
            fan_command.append(0)

        if request.data["fanAir2"] == True:
            fan_command.append(1)
        else:
            fan_command.append(0)
        z = fan_command
        try:
            if request.data["fanspeed"] == 'low':
                fan_command.clear()
                fan_command.append(0)
                fan_command.append(0)
            if request.data["fanspeed"] == 'medium':
                fan_command.clear()
                fan_command.append(1)
                fan_command.append(0)
            if request.data["fanspeed"] == 'high':
                fan_command.clear()
                fan_command.append(0)
                fan_command.append(1)
        except:
            pass

        client = mqtt.Client()
        z = Node.objects.filter(id=int(request.data["nodeid"]))[0].MacAddress
        dictsend = {
            "type": "33",
            "time": "568595",
            "conf": [
                {
                    "id": z,
                    "setT": [int(request.data["temp"]), int(request.data["dongleValue1"]),
                             int(request.data["dongleValue2"]), 255],
                    "valve_command": valve_cammand,
                    "workmode": c,
                    "permission": b,
                    "hvac": 1,
                    "speed": 1,
                    "fan_command": fan_command,
                }
            ],
            "equ": {}
        }
        # print('inam bekhatere roya', z)
        json_object = json.dumps(dictsend)
        print(json_object)
        client.connect('98.91.15.243', 1700)
        client.publish('scps/server/2', json_object)

    def handle_valve(self, timer, target):
        time.sleep(timer)
        self.request.data[target] = False
        self.change_valves()

    def post(self, request):
        self.request = request
        if not self.request.data['cValve1'] and self.request.data['cValve1Time'] > 0:
            threading.Thread(target=self.handle_valve, args=(self.request.data['cValve1Time'], 'cValve1')).start()
        if not self.request.data['cValve2'] and self.request.data['cValve2Time'] > 0:
            threading.Thread(target=self.handle_valve, args=(self.request.data['cValve2Time'], 'cValve2')).start()
        if not self.request.data['fanAir1'] and self.request.data['fanAir1Time'] > 0:
            threading.Thread(target=self.handle_valve, args=(self.request.data['fanAir1Time'], 'fanAir1')).start()
        if not self.request.data['fanAir2'] and self.request.data['fanAir2Time'] > 0:
            threading.Thread(target=self.handle_valve, args=(self.request.data['fanAir2Time'], 'fanAir2')).start()
        self.request.data['cValve1'] = self.request.data['cValve1'] or bool(self.request.data['cValve1Time'])
        self.request.data['cValve2'] = self.request.data['cValve2'] or bool(self.request.data['cValve2Time'])
        self.request.data['fanAir1'] = self.request.data['fanAir1'] or bool(self.request.data['fanAir1Time'])
        self.request.data['fanAir2'] = self.request.data['fanAir2'] or bool(self.request.data['fanAir2Time'])
        self.change_valves()
        return Response(status=status.HTTP_200_OK)


class MqttRunCommand(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        x = threading.Thread(target=MqttRun)
        x.start()
        return Response(status=status.HTTP_200_OK)


class graphNodes(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # TODO
        nodes = []
        links = []
        for t in Node.objects.all():
            p = {
                'id': str(t.id)
            }
            nodes.append(p)
        o = {
            'id': '0'
        }
        nodes.append(o)
        #    for n in Neighbor.objects.all():
        #        o = {
        #            'source': str(n.Node1.id),
        #            'target': str(n.Node2.id)
        #        }
        # links.append(o)
        data = {'graph': nodes, 'links': links}
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'graph',
                'message': json.dumps(data)
            }
        )
        return Response(status=status.HTTP_200_OK)


class controlPanel(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # print(request.data)
        hvacmode = request.data['hvacmode']
        selectmode = request.data['selectmode']
        fan = request.data['fan']
        m = 0
        setpoint = ""
        if selectmode == 'sleep':
            setpoint = 20
            m = 0
        else:
            setpoint = int(request.data['setpoint'])
        if selectmode == 'classic':
            m = 4
        if selectmode == 'energysaving':
            m = 1
        if selectmode == 'maintenance':
            m = 2
        if hvacmode == "cooling":
            h = 1
        else:
            h = 0
        dictsend = {
            "type": "33",
            "time": "568595",
            "conf": [
                {
                    "id": "ff:ff:ff:ff:ff:ff",
                    "setT": [setpoint, 255, 255, 255],
                    "valve_command": [1, 1],
                    "workmode": m,
                    "permission": "1",
                    "hvac": h,
                    "fan_command": [1, 1],
                }
            ],
            "equ": {}
        }
        json_object = json.dumps(dictsend)
        print(json_object)
        client.connect('98.91.15.243', 1700)
        client.publish('scps/server/1', json_object)
        return Response(status=status.HTTP_200_OK)


class Floor(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        parser_classes = [MultiPartParser, FormParser]
        serializer = Floorserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        f = Floor.objects.all()
        serializer = Floorserializer(data=f, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class weather(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        city_name = request.data["city_name"]
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=60d02a8e8559a6937eb7f31c672e18ba&units=metric'.format(
            city_name)
        res = requests.get(url)
        data = res.json()
        if not 'rain' in data: data['rain'] = {}
        if not '1h' in data['rain']: data['rain']['1h'] = 0
        json_object = json.dumps(data)
        print(json_object)
        return Response(data=json_object, status=status.HTTP_200_OK)


class ReportNodeStation(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ffrom = request.data['from'].split("-")
        datef = datetime(int(ffrom[0]), int(ffrom[1]), int(ffrom[2]))
        to = request.data['to'].split("-")
        datet = datetime(int(to[0]), int(to[1]), int(to[2]))
        node = request.data['nodeid']
        MyNode = Node.objects.get(id=int(node))
        l = NodeStation.objects.filter(Node=MyNode)
        s = 0
        t = 0
        times = []
        temps = []
        for i in l:
            if i.DateTime.year == datet.year and i.DateTime.month == datet.month and i.DateTime.day == datet.day + 1:
                break
            if (
                    i.DateTime.year == datef.year and i.DateTime.month == datef.month and i.DateTime.day == datef.day) or s == 1:
                s == 1
                if t == 0:
                    times.append(str(i.DateTime))
                    temps.append(str(i.HomeTemperature))
                t = t + 1
                if t == 10:
                    t = 0

        data = {'nodeid': str(MyNode.id), 'times': times, 'temps': temps}

        # z=l.filter(HomeTemperature>datef and HomeTemperature<datet)
        return Response(data=data, status=status.HTTP_200_OK)


class ReportSecurityStation(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ffrom = request.data['from'].split("-")
        datef = datetime(int(ffrom[0]), int(ffrom[1]), int(ffrom[2]))
        to = request.data['to'].split("-")
        datet = datetime(int(to[0]), int(to[1]), int(to[2]))
        l = NodeStation.objects.all()
        s = 0
        t = 0
        data = []
        for i in l:
            if i.DateTime.year == datet.year and i.DateTime.month == datet.month and i.DateTime.day == datet.day + 1:
                break
            if (
                    i.DateTime.year == datef.year and i.DateTime.month == datef.month and i.DateTime.day == datef.day) or s == 1:
                s == 1
                if t == 0:
                    light = ""
                    humidity = ""
                    analog1 = ""
                    analog2 = ""
                    if i.light == -1 or i.light == 65535 or i.light is None:
                        light = "Null"
                    else:
                        light = i.light
                    if i.humidity == 255:
                        humidity = "Null"
                    else:
                        humidity = i.humidity
                    if i.analog1 == 65535:
                        analog1 = "Null"
                    else:
                        analog1 = i.analog1
                    if i.analog2 == 65535:
                        analog2 = "Null"
                    else:
                        analog2 = i.analog2
                    bn = {
                        "Time": str(i.DateTime),
                        "ID": str(i.id),
                        "RoomTemp": str(i.HomeTemperature),
                        "Humidity": humidity,
                        "Light": light,
                        "AnalogSensor1": analog1,
                        "AnalogSensor2": analog2,
                        "WorkMode": "sleep",
                        "UserSetPoint": "20",
                        "HVACType1": "NULL",
                        "HVACSetPoint1": "30",
                        "HVACTemp1": "30",
                        "HVACState1": "1",
                        "HVACType2": "NULL",
                        "HVACSetPoint2": "30",
                        "HVACTemp2": "30",
                        "HVACState2": "1"
                    }
                    data.append(bn)
                t = t + 1
                if t == 10:
                    t = 0
        return Response(data=[], status=status.HTTP_200_OK)


class ReportRoomTem(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ffrom = request.data['from'].split("-")
        datef = datetime(int(ffrom[0]), int(ffrom[1]), int(ffrom[2]))
        to = request.data['to'].split("-")
        datet = datetime(int(to[0]), int(to[1]), int(to[2]))
        l = NodeStation.objects.all()
        s = 0
        t = 0
        data = []
        for i in l:
            if i.DateTime.year == datet.year and i.DateTime.month == datet.month and i.DateTime.day == datet.day + 1:
                break
            if (
                    i.DateTime.year == datef.year and i.DateTime.month == datef.month and i.DateTime.day == datef.day) or s == 1:
                s == 1
                if t == 0:
                    light = ""
                    humidity = ""
                    analog1 = ""
                    analog2 = ""
                    if i.light == -1 or i.light == 65535 or i.light is None:
                        light = "Null"
                    else:
                        light = int(i.light * 100) / 100
                    if i.humidity == 255:
                        humidity = "Null"
                    else:
                        humidity = i.humidity
                    if i.analog1 == 65535:
                        analog1 = "Null"
                    else:
                        analog1 = i.analog1
                    if i.analog2 == 65535:
                        analog2 = "Null"
                    else:
                        analog2 = i.analog2
                    bn = {
                        "Time": str(i.DateTime),
                        "ID": str(i.Node.id),
                        "RoomTemp": str(i.HomeTemperature),
                        "Humidity": humidity,
                        "Light": light,
                        "AnalogSensor1": analog1,
                        "AnalogSensor2": analog2,
                        "WorkMode": "sleep",
                        "UserSetPoint": "20",
                        "HVACType1": "NULL",
                        "HVACSetPoint1": "30",
                        "HVACTemp1": "30",
                        "HVACState1": "1",
                        "HVACType2": "NULL",
                        "HVACSetPoint2": "30",
                        "HVACTemp2": "30",
                        "HVACState2": "1"
                    }
                    data.append(bn)
                t = t + 1
                if t == 10:
                    t = 0
        return Response(data=data, status=status.HTTP_200_OK)


class MatFiled(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        parser_classes = [MultiPartParser, FormParser]
        serializer = MatFileserializer(data=request.data)
        if serializer.is_valid():
            print("1111111111111111111111111111111111111111111111111111111")
            serializer.save()
            print("22222222222222222222222222222222")
            f = MatFile.objects.all()
            a = "http://37.156.25.234:8000/" + str(f[0].File)
            print(a)
            dictsend = {
                "type": "11",
                "time": "server timestamp",
                "clusters": [
                    {
                        "CHId": "<device mac address>",
                        "channel": "5"
                    }
                ],
                "equ": {"url": a},
                "conf": [
                    {
                        "id": "<device mac address>",
                        "setT": [25, 255, 255, 255],
                        "permission": 0,
                        "workmode": 1,
                        "hvac": 0,
                        "fan_command": [],
                        "Valve_command": [],
                        "out_temp": 40,
                        "engine_temp": 35,
                        "other_temp": 27,

                    }
                ]
            }
            json_object = json.dumps(dictsend)
            print(json_object)
            client.connect('98.91.15.243', 1700)
            client.publish('scps/server', json_object)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(request.data, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        f = MatFile.objects.all()
        serializer = MatFileserializer(data=f, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
