from rest_framework import serializers
from .models import Wallet, Transaction


class WalletSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Wallet
        fields = ["id", "user_email", "currency", "balance", "is_demo", "updated_at"]


class TransactionSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source="sender.email", read_only=True, allow_null=True)
    recipient_email = serializers.EmailField(source="recipient.email", read_only=True, allow_null=True)

    class Meta:
        model = Transaction
        fields = ["reference", "sender_email", "recipient_email", "amount", "fee", "currency",
                  "kind", "status", "description", "created_at", "completed_at"]
        read_only_fields = fields
