from decimal import Decimal, InvalidOperation

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer
from .services import transfer_funds, topup_demo, get_or_create_wallet
from audit.models import AuditLog


class WalletDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        wallet = get_or_create_wallet(request.user)
        return Response(WalletSerializer(wallet).data)


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from django.db.models import Q
        from django.utils.dateparse import parse_date
        from decimal import Decimal, InvalidOperation
        user = self.request.user
        qs = Transaction.objects.filter(Q(sender=user) | Q(recipient=user))
        p = self.request.query_params
        kind = p.get("kind")
        if kind:
            qs = qs.filter(kind=kind)
        status_v = p.get("status")
        if status_v:
            qs = qs.filter(status=status_v)
        recipient = p.get("recipient")
        if recipient:
            qs = qs.filter(recipient__email__icontains=recipient)
        sender = p.get("sender")
        if sender:
            qs = qs.filter(sender__email__icontains=sender)
        q = p.get("q")
        if q:
            qs = qs.filter(Q(description__icontains=q) | Q(reference__icontains=q))
        dfrom = p.get("from")
        if dfrom:
            dd = parse_date(dfrom)
            if dd:
                qs = qs.filter(created_at__date__gte=dd)
        dto = p.get("to")
        if dto:
            dd = parse_date(dto)
            if dd:
                qs = qs.filter(created_at__date__lte=dd)
        for field, key in (("min_amount", "amount__gte"), ("max_amount", "amount__lte")):
            v = p.get(field)
            if v:
                try:
                    qs = qs.filter(**{key: Decimal(v)})
                except (InvalidOperation, ValueError):
                    pass
        return qs.order_by("-created_at")


class TransferView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        recipient = request.data.get("recipient_email")
        amount = request.data.get("amount")
        description = request.data.get("description", "")
        idempotency_key = request.data.get("idempotency_key")
        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            return Response({"detail": "Montant invalide."}, status=status.HTTP_400_BAD_REQUEST)
        if amount <= 0:
            return Response({"detail": "Le montant doit être supérieur à zéro."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tx = transfer_funds(request.user, recipient, amount, description, idempotency_key, _ip(request))
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "Erreur lors du transfert."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)


class TopupDemoView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        amount = request.data.get("amount", "100000")
        try:
            amount = Decimal(str(amount))
        except Exception:
            return Response({"detail": "Montant invalide."}, status=status.HTTP_400_BAD_REQUEST)
        if amount <= 0 or amount > Decimal("1000000"):
            return Response({"detail": "Montant hors limites démo."}, status=status.HTTP_400_BAD_REQUEST)
        tx = topup_demo(request.user, amount, _ip(request))
        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)


class TransactionDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, reference):
        try:
            tx = Transaction.objects.get(reference=reference)
        except Transaction.DoesNotExist:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        if tx.sender != request.user and tx.recipient != request.user:
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)
        return Response(TransactionSerializer(tx).data)


def _ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
