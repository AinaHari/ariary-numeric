import hashlib
import os

from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BlockchainRecord
from .serializers import BlockchainRecordSerializer


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def blockchain_status():
    rpc = getattr(settings, "BLOCKCHAIN_RPC_URL", "")
    if not rpc:
        return "non_configure", "Blockchain de test non configurée"
    try:
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 5}))
        if w3.is_connected():
            return "configure", f"Connecté au réseau (chainId={w3.eth.chain_id})"
        return "non_configure", "Blockchain de test non configurée"
    except Exception:
        return "non_configure", "Blockchain de test non configurée"


class BlockchainInfoView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        st, msg = blockchain_status()
        return Response({
            "network": "sepolia" if settings.BLOCKCHAIN_CHAIN_ID == 11155111 else str(settings.BLOCKCHAIN_CHAIN_ID),
            "chain_id": settings.BLOCKCHAIN_CHAIN_ID,
            "rpc_configured": bool(settings.BLOCKCHAIN_RPC_URL),
            "status": st,
            "message": msg,
            "contract_address": settings.BLOCKCHAIN_CONTRACT_ADDRESS or None,
        })


class BlockchainRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = BlockchainRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return BlockchainRecord.objects.all().order_by("-created_at")

    def post(self, request, *args, **kwargs):
        record_type = request.data.get("record_type", "document")
        payload = request.data.get("payload", "")
        data_hash = request.data.get("data_hash") or sha256_hex(str(payload))
        st, _ = blockchain_status()
        initial_status = "en_attente" if st == "configure" else "non_configure"
        rec = BlockchainRecord.objects.create(
            record_type=record_type,
            data_hash=data_hash,
            network="sepolia",
            status=initial_status,
            metadata={"payload_preview": str(payload)[:200]},
        )
        return Response({
            "id": rec.id,
            "record_type": rec.record_type,
            "data_hash": rec.data_hash,
            "status": rec.status,
            "message": "Blockchain de test non configurée" if rec.status == "non_configure" else "Empreinte enregistrée (en attente de confirmation réseau).",
        }, status=status.HTTP_201_CREATED)


class BlockchainVerifyView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data_hash = request.data.get("data_hash")
        payload = request.data.get("payload")
        reference = request.data.get("reference")
        if payload is not None and not data_hash:
            data_hash = sha256_hex(str(payload))
        rec = None
        if data_hash:
            rec = BlockchainRecord.objects.filter(data_hash=data_hash).first()
            if not rec:
                return Response({"verified": False, "detail": "Empreinte inconnue."}, status=status.HTTP_404_NOT_FOUND)
            recomputed = sha256_hex(str(payload)) if payload is not None else data_hash
            ok = recomputed == rec.data_hash
            return Response({"verified": ok, "record_id": rec.id, "status": rec.status, "data_hash": rec.data_hash})
        if reference:
            for r in BlockchainRecord.objects.filter(metadata__reference=str(reference)):
                return Response({
                    "verified": True,
                    "note": "Transaction enregistrée dans le registre de test.",
                    "record_id": r.id,
                    "status": r.status,
                    "data_hash": r.data_hash,
                    "metadata": r.metadata,
                })
            return Response({"verified": False, "detail": "Référence inconnue dans le registre."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"verified": False, "detail": "Fournir 'payload', 'data_hash' ou 'reference'."}, status=status.HTTP_400_BAD_REQUEST)


class BlockchainRecordDetailView(generics.RetrieveAPIView):
    serializer_class = BlockchainRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = BlockchainRecord.objects.all()
