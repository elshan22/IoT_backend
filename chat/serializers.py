from rest_framework import serializers
from .models import Node, State


class GraphSetting(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = '__all__'


class NodeState(serializers.ModelSerializer):
    # node_id = serializers.ReadOnlyField(source='node.id',read_only=True)
    print("node_id")

    class Meta:
        model = State
        fields = '__all__'

    def to_representation(self, instance):
        print(instance)
        representation = dict()
        representation["id"] = instance.id
        representation["Node"] = instance.Node.id
        representation["DateTime"] = instance.DateTime
        representation["temperature"] = instance.temperature
