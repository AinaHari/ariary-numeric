from rest_framework import serializers
from .models import ExchangeRate, InternationalTransfer, PaymentConnector

class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = "__all__"

class InternationalTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternationalTransfer
        fields = "__all__"

class PaymentConnectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentConnector
        fields = "__all__"
