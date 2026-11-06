import hashlib
import os

from django.conf import settings
from django.utils import timezone
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


def get_web3_and_contract():
    """Return (w3, contract) if RPC and contract are configured, else (None, None)."""
    rpc = getattr(settings, "BLOCKCHAIN_RPC_URL", "")
    contract_address = getattr(settings, "BLOCKCHAIN_CONTRACT_ADDRESS", "")
    private_key = getattr(settings, "BLOCKCHAIN_PRIVATE_KEY", "")
    if not rpc or not contract_address or not private_key:
        return None, None
    try:
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 10}))
        if not w3.is_connected():
            return None, None
        # Minimal ABI for AriaryRegistry
        abi = [
            {"inputs": [{"name": "h", "type": "bytes32"}], "name": "record", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
            {"inputs": [{"name": "h", "type": "bytes32"}], "name": "verify", "outputs": [{"name": "", "type": "bool"}], "stateMutability": "view", "type": "function"},
            {"inputs": [{"name": "", "type": "bytes32"}], "name": "exists", "outputs": [{"name": "", "type": "bool"}], "stateMutability": "view", "type": "function"},
        ]
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)
        return w3, contract
    except Exception:
        return None, None


def record_on_chain(data_hash_hex: str) -> str:
    """Send a transaction to record the hash on-chain. Returns tx_hash or empty string."""
    w3, contract = get_web3_and_contract()
    if not w3 or not contract:
        return ""
    try:
        from web3 import Web3
        private_key = settings.BLOCKCHAIN_PRIVATE_KEY
        account = w3.eth.account.from_key(private_key)
        hash_bytes = bytes.fromhex(data_hash_hex)
        # pad to 32 bytes if needed
        if len(hash_bytes) < 32:
            hash_bytes = hash_bytes.ljust(32, b'\x00')
        elif len(hash_bytes) > 32:
            hash_bytes = hash_bytes[:32]
        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.record(hash_bytes).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": w3.eth.gas_price,
            "chainId": settings.BLOCKCHAIN_CHAIN_ID,
        })
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        return tx_hash.hex()
    except Exception:
        return ""


def verify_on_chain(data_hash_hex: str) -> bool | None:
    """Verify a hash on-chain. Returns True/False if on-chain, None if not configured."""
    w3, contract = get_web3_and_contract()
    if not w3 or not contract:
        return None
    try:
        from web3 import Web3
        hash_bytes = bytes.fromhex(data_hash_hex)
        if len(hash_bytes) < 32:
            hash_bytes = hash_bytes.ljust(32, b'\x00')
        elif len(hash_bytes) > 32:
            hash_bytes = hash_bytes[:32]
        return contract.functions.verify(hash_bytes).call()
    except Exception:
        return None


def check_tx_receipt(tx_hash: str) -> str:
    """Check transaction receipt. Returns 'confirmed', 'failed', or 'pending'."""
    w3, contract = get_web3_and_contract()
    if not w3:
        return "pending"
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if receipt is None:
            return "pending"
        if receipt.status == 1:
            return "confirmed"
        return "failed"
    except Exception:
        return "pending"
    """Verify a hash on-chain. Returns True/False if on-chain, None if not configured."""
    w3, contract = get_web3_and_contract()
    if not w3 or not contract:
        return None
    try:
        from web3 import Web3
        hash_bytes = bytes.fromhex(data_hash_hex)
        if len(hash_bytes) < 32:
            hash_bytes = hash_bytes.ljust(32, b'\x00')
        elif len(hash_bytes) > 32:
            hash_bytes = hash_bytes[:32]
        return contract.functions.verify(hash_bytes).call()
    except Exception:
        return None


class BlockchainInfoView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        st, msg = blockchain_status()
        w3, contract = get_web3_and_contract()
        return Response({
            "network": "sepolia" if settings.BLOCKCHAIN_CHAIN_ID == 11155111 else str(settings.BLOCKCHAIN_CHAIN_ID),
            "chain_id": settings.BLOCKCHAIN_CHAIN_ID,
            "rpc_configured": bool(settings.BLOCKCHAIN_RPC_URL),
            "contract_configured": bool(settings.BLOCKCHAIN_CONTRACT_ADDRESS and settings.BLOCKCHAIN_PRIVATE_KEY),
            "on_chain_enabled": w3 is not None,
            "status": st,
            "message": msg,
            "contract_address": settings.BLOCKCHAIN_CONTRACT_ADDRESS or None,
        })


class BlockchainRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = BlockchainRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return BlockchainRecord.objects.filter(owner=self.request.user).order_by("-created_at")

    def post(self, request, *args, **kwargs):
        record_type = request.data.get("record_type", "document")
        payload = request.data.get("payload", "")
        data_hash = request.data.get("data_hash") or sha256_hex(str(payload))
        st, _ = blockchain_status()
        initial_status = "en_attente" if st == "configure" else "non_configure"
        rec = BlockchainRecord.objects.create(
            owner=request.user,
            record_type=record_type,
            data_hash=data_hash,
            network="sepolia",
            status=initial_status,
            metadata={"payload_preview": str(payload)[:200]},
        )
        # Attempt on-chain recording if RPC + contract + key are configured
        tx_hash = record_on_chain(data_hash)
        if tx_hash:
            rec.tx_hash = tx_hash
            rec.status = BlockchainRecord.STATUS_PENDING
            rec.save(update_fields=["tx_hash", "status"])
        return Response({
            "id": rec.id,
            "record_type": rec.record_type,
            "data_hash": rec.data_hash,
            "status": rec.status,
            "tx_hash": rec.tx_hash or None,
            "message": "Empreinte envoyée sur la blockchain de test (Sepolia)." if tx_hash else ("Blockchain de test non configurée" if rec.status == "non_configure" else "Empreinte enregistrée (en attente de confirmation réseau)."),
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
            rec = BlockchainRecord.objects.filter(owner=request.user, data_hash=data_hash).first()
            if not rec:
                return Response({"verified": False, "detail": "Empreinte inconnue."}, status=status.HTTP_404_NOT_FOUND)
            # Try on-chain verification first
            on_chain = verify_on_chain(data_hash)
            if on_chain is not None:
                # Also check receipt status if tx_hash exists
                receipt_status = None
                if rec.tx_hash:
                    receipt_status = check_tx_receipt(rec.tx_hash)
                    if receipt_status == "confirmed" and rec.status != BlockchainRecord.STATUS_CONFIRMED:
                        rec.status = BlockchainRecord.STATUS_CONFIRMED
                        rec.confirmed_at = timezone.now()
                        rec.save(update_fields=["status", "confirmed_at"])
                    elif receipt_status == "failed" and rec.status != BlockchainRecord.STATUS_FAILED:
                        rec.status = BlockchainRecord.STATUS_FAILED
                        rec.save(update_fields=["status"])
                return Response({"verified": on_chain, "record_id": rec.id, "status": rec.status, "data_hash": rec.data_hash, "on_chain": True, "receipt_status": receipt_status})
            recomputed = sha256_hex(str(payload)) if payload is not None else data_hash
            ok = recomputed == rec.data_hash
            return Response({"verified": ok, "record_id": rec.id, "status": rec.status, "data_hash": rec.data_hash, "on_chain": False})
        if reference:
            for r in BlockchainRecord.objects.filter(owner=request.user, metadata__reference=str(reference)):
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

    def get_queryset(self):
        return BlockchainRecord.objects.filter(owner=self.request.user)


class BlockchainRefreshView(APIView):
    """Refresh confirmation status of pending records based on transaction receipts."""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        updated = 0
        for rec in BlockchainRecord.objects.filter(owner=request.user, status=BlockchainRecord.STATUS_PENDING).exclude(tx_hash=""):
            result = check_tx_receipt(rec.tx_hash)
            if result == "confirmed":
                rec.status = BlockchainRecord.STATUS_CONFIRMED
                rec.confirmed_at = timezone.now()
                rec.save(update_fields=["status", "confirmed_at"])
                updated += 1
            elif result == "failed":
                rec.status = BlockchainRecord.STATUS_FAILED
                rec.save(update_fields=["status"])
                updated += 1
        return Response({"updated": updated, "checked": BlockchainRecord.objects.filter(owner=request.user, status=BlockchainRecord.STATUS_PENDING).count()})
    """Refresh confirmation status of pending records based on transaction receipts."""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        updated = 0
        for rec in BlockchainRecord.objects.filter(owner=request.user, status=BlockchainRecord.STATUS_PENDING).exclude(tx_hash=""):
            result = check_tx_receipt(rec.tx_hash)
            if result == "confirmed":
                rec.status = BlockchainRecord.STATUS_CONFIRMED
                rec.confirmed_at = timezone.now()
                rec.save(update_fields=["status", "confirmed_at"])
                updated += 1
            elif result == "failed":
                rec.status = BlockchainRecord.STATUS_FAILED
                rec.save(update_fields=["status"])
                updated += 1
        return Response({"updated": updated, "checked": BlockchainRecord.objects.filter(owner=request.user, status=BlockchainRecord.STATUS_PENDING).count()})
    serializer_class = BlockchainRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return BlockchainRecord.objects.filter(owner=self.request.user)
