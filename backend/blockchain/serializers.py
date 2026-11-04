"""Serializers pour le module blockchain (empreintes de test)."""
from rest_framework import serializers

from .models import BlockchainRecord


class BlockchainRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockchainRecord
        fields = ["id", "record_type", "data_hash", "network", "tx_hash",
                  "status", "metadata", "created_at", "confirmed_at"]
        read_only_fields = fields
