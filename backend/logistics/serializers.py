from rest_framework import serializers
from .models import Shipment, ShipmentEvent, ShipmentDocument


class ShipmentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentEvent
        fields = ["id", "status", "location", "description", "source", "created_at"]
        read_only_fields = ["id", "created_at"]


class ShipmentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentDocument
        fields = ["id", "name", "file", "created_at"]
        read_only_fields = ["id", "created_at"]


class ShipmentSerializer(serializers.ModelSerializer):
    events = ShipmentEventSerializer(many=True, read_only=True)
    documents = ShipmentDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = ["reference", "name", "origin", "destination", "mode", "carrier",
                  "tracking_number", "estimated_departure", "estimated_arrival", "status",
                  "notes", "events", "documents", "created_at", "updated_at"]
        read_only_fields = ["reference", "created_at", "updated_at"]


class ShipmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ["name", "origin", "destination", "mode", "carrier", "tracking_number",
                  "estimated_departure", "estimated_arrival", "notes"]
