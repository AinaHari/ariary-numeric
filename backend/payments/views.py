from decimal import Decimal, InvalidOperation
import uuid

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ExchangeRate, InternationalTransfer, PaymentConnector
from .serializers import ExchangeRateSerializer, InternationalTransferSerializer, PaymentConnectorSerializer


class ExchangeRateListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer


class EstimateInternationalTransferView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        origin_country = request.data.get("origin_country", "Madagascar")
        destination_country = request.data.get("destination_country", "")
        origin_currency = request.data.get("origin_currency", "MGA")
        destination_currency = request.data.get("destination_currency", "EUR")
        amount = request.data.get("amount")
        try:
            amount = Decimal(str(amount))
        except Exception:
            return Response({"detail": "Montant invalide."}, status=status.HTTP_400_BAD_REQUEST)
        if amount <= 0:
            return Response({"detail": "Montant invalide."}, status=status.HTTP_400_BAD_REQUEST)

        rate_obj = ExchangeRate.objects.filter(base=origin_currency, target=destination_currency).first()
        if rate_obj:
            rate = rate_obj.rate
            source = rate_obj.source
        else:
            # demo rate clearly identified
            rate = Decimal("0.0021")
            source = "taux de démonstration (non réel)"
        fee = (amount * Decimal("0.02")).quantize(Decimal("0.01"))
        # Montant reçu = (montant - frais) converti au taux
        receive = ((amount - fee) * rate).quantize(Decimal("0.01"))
        it = InternationalTransfer.objects.create(
            reference=f"INT-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
            owner=request.user,
            origin_country=origin_country,
            destination_country=destination_country,
            origin_currency=origin_currency,
            destination_currency=destination_currency,
            amount=amount,
            rate=rate,
            estimated_fee=fee,
            estimated_receive=receive,
            status=InternationalTransfer.STATUS_ESTIMATED,
        )
        return Response({
            "reference": it.reference,
            "origin_country": origin_country,
            "destination_country": destination_country,
            "origin_currency": origin_currency,
            "destination_currency": destination_currency,
            "amount": str(amount),
            "rate": str(rate),
            "rate_source": source,
            "rate_updated_at": rate_obj.updated_at.isoformat() if rate_obj else None,
            "estimated_fee": str(fee),
            "estimated_receive": str(receive),
            "status": it.status,
            "note": "Transferts internationaux réels désactivés : partenaire de paiement autorisé requis.",
            "real_transfers_enabled": False,
        })


class InternationalTransferListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = InternationalTransferSerializer

    def get_queryset(self):
        return InternationalTransfer.objects.filter(owner=self.request.user)


class PaymentConnectorListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PaymentConnectorSerializer

    def get_queryset(self):
        return PaymentConnector.objects.all()


class MobileMoneyInfoView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response({
            "available": False,
            "message": "Paiements mobile money réels non disponibles dans cette version",
            "connectors": list(PaymentConnector.objects.filter(kind="mobile_money").values("name", "is_active")),
        })
