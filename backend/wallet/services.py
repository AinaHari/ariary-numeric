from decimal import Decimal
from django.db import IntegrityError, transaction as db_transaction
from django.utils import timezone

from audit.models import AuditLog
from ledger.models import LedgerEntry
from notifications.models import Notification
from .models import Wallet, Transaction


def get_or_create_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


def fingerprint_transaction(tx):
    """Enregistre une empreinte blockchain de test pour une transaction clôturée."""
    from blockchain.models import BlockchainRecord

    try:
        data_hash = sha256_hex(
            f"ariary|{tx.reference}|{tx.kind}|{tx.amount}|{tx.currency}"
        )
        BlockchainRecord.objects.get_or_create(
            data_hash=data_hash,
            defaults={
                "record_type": "transaction",
                "network": "sepolia",
                "status": BlockchainRecord.STATUS_UNCONFIGURED,
                "metadata": {
                    "reference": str(tx.reference),
                    "kind": tx.kind,
                    "amount": str(tx.amount),
                    "currency": tx.currency,
                    "description": (tx.description or "")[:120],
                },
            },
        )
    except Exception:
        # L'empreinte ne doit jamais bloquer la transaction elle-même.
        pass


def sha256_hex(data: str) -> str:
    import hashlib
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def record_audit(actor, action, target_type="", target_id="", metadata=None, ip=None):
    AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else "",
        metadata=metadata or {},
        ip_address=ip,
    )


def transfer_funds(sender, recipient_email, amount, description="", idempotency_key=None, ip=None):
    """Demonstration internal transfer between two users. Atomic with idempotency."""
    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValueError("Le montant doit être supérieur à zéro.")

    # Chemin rapide (lecture seule) : le contrôle définitif a lieu dans la transaction.
    if idempotency_key:
        existing = Transaction.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return existing

    recipient = None
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        recipient = User.objects.get(email=recipient_email.strip().lower())
    except User.DoesNotExist:
        raise ValueError("Destinataire introuvable.")

    if recipient == sender:
        raise ValueError("Impossible de transférer vers soi-même.")

    sender_wallet = get_or_create_wallet(sender)
    recipient_wallet = get_or_create_wallet(recipient)

    try:
        with db_transaction.atomic():
            # lock rows
            sw = Wallet.objects.select_for_update().get(pk=sender_wallet.pk)
            rw = Wallet.objects.select_for_update().get(pk=recipient_wallet.pk)

            # idempotence: revérifié sous verrous avant toute écriture
            if idempotency_key:
                existing = Transaction.objects.filter(idempotency_key=idempotency_key).first()
                if existing:
                    return existing

            if sw.balance < amount:
                raise ValueError("Solde insuffisant.")

            sw.balance = sw.balance - amount
            rw.balance = rw.balance + amount
            sw.save(update_fields=["balance", "updated_at"])
            rw.save(update_fields=["balance", "updated_at"])

            tx = Transaction.objects.create(
                sender=sender,
                recipient=recipient,
                sender_wallet=sw,
                recipient_wallet=rw,
                amount=amount,
                currency=sw.currency,
                kind=Transaction.KIND_TRANSFER,
                status=Transaction.STATUS_COMPLETED,
                description=description,
                idempotency_key=idempotency_key,
                completed_at=timezone.now(),
            )
            LedgerEntry.objects.create(transaction=tx, wallet=sw, entry_type=LedgerEntry.ENTRY_DEBIT, amount=amount, balance_after=sw.balance)
            LedgerEntry.objects.create(transaction=tx, wallet=rw, entry_type=LedgerEntry.ENTRY_CREDIT, amount=amount, balance_after=rw.balance)
    except IntegrityError:
        # Deux requêtes simultanées avec la même clé : la contrainte unique départage.
        if idempotency_key:
            return Transaction.objects.filter(idempotency_key=idempotency_key).first()
        raise

    record_audit(sender, "transfer.completed", "Transaction", tx.reference, {"amount": str(amount), "recipient": recipient.email}, ip)
    # notifications
    Notification.objects.create(user=recipient, ntype=Notification.TYPE_TRANSFER_RECEIVED, title="Transfert reçu",
                               message=f"Vous avez reçu {amount} {sw.currency} de {sender.email}. Réf: {tx.reference}")
    Notification.objects.create(user=sender, ntype=Notification.TYPE_TRANSFER_SENT, title="Transfert envoyé",
                               message=f"Vous avez envoyé {amount} {sw.currency} à {recipient.email}. Réf: {tx.reference}")
    fingerprint_transaction(tx)
    return tx


def topup_demo(user, amount, ip=None):
    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValueError("Montant invalide.")
    wallet = get_or_create_wallet(user)
    with db_transaction.atomic():
        w = Wallet.objects.select_for_update().get(pk=wallet.pk)
        w.balance = w.balance + amount
        w.save(update_fields=["balance", "updated_at"])
        tx = Transaction.objects.create(
            recipient=user,
            recipient_wallet=w,
            amount=amount,
            currency=w.currency,
            kind=Transaction.KIND_TOPUP,
            status=Transaction.STATUS_COMPLETED,
            description="Rechargement portefeuille de démonstration",
            completed_at=timezone.now(),
        )
        LedgerEntry.objects.create(transaction=tx, wallet=w, entry_type=LedgerEntry.ENTRY_CREDIT, amount=amount, balance_after=w.balance)
    record_audit(user, "wallet.topup_demo", "Transaction", tx.reference, {"amount": str(amount)}, ip)
    fingerprint_transaction(tx)
    return tx
