import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

User = get_user_model()

from ledger.models import LedgerEntry
from notifications.models import Notification
from wallet.models import Transaction, Wallet

# PBKDF2 est trop lent sur cette machine (~9 s par hachage).
# Django recommande un hachage de test rapide : https://docs.djangoproject.com/en/stable/topics/testing/advanced/#speeding-up-tests
FAST_PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Désactiver la limitation de débit pendant les tests (sinon les 49 tests dépassent 10/min).
FAST_THROTTLE_RATES = {"anon": "10000/min", "user": "10000/min", "login": "10000/min", "guest": "10000/min"}


class BaseTestCase(TestCase):
    """TestCase avec hachage de mot de passe rapide (répété ~40 fois dans la suite)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.enterClassContext(override_settings(PASSWORD_HASHERS=FAST_PASSWORD_HASHERS))
        cls.enterClassContext(override_settings(REST_FRAMEWORK={
            "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication", "rest_framework.authentication.TokenAuthentication"),
            "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
            "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
            "PAGE_SIZE": 20,
            "DEFAULT_THROTTLE_RATES": FAST_THROTTLE_RATES,
        }))


def make_user(email="u@example.com", password="TestPass123!"):
    return User.objects.create_user(email=email, password=password)


class AuthTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_and_login(self):
        r = self.client.post("/api/v1/accounts/register/", {
            "email": "a@example.com", "password": "TestPass123!", "password_confirm": "TestPass123!"
        })
        self.assertEqual(r.status_code, 201)
        self.assertIn("token", r.json())
        r2 = self.client.post("/api/v1/accounts/login/", {"email": "a@example.com", "password": "TestPass123!"})
        self.assertEqual(r2.status_code, 200)

    def test_login_invalid(self):
        make_user("b@example.com")
        r = self.client.post("/api/v1/accounts/login/", {"email": "b@example.com", "password": "wrong"})
        self.assertEqual(r.status_code, 401)

    def test_profile_requires_auth(self):
        r = self.client.get("/api/v1/accounts/me/")
        self.assertIn(r.status_code, (401, 403))


class WalletTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = make_user("s@example.com")
        self.u2 = make_user("r@example.com")
        r = self.client.post("/api/v1/accounts/login/", {"email": "s@example.com", "password": "TestPass123!"})
        self.token = r.json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_topup_and_transfer(self):
        r = self.client.post("/api/v1/wallet/topup-demo/", {"amount": "1000"})
        self.assertEqual(r.status_code, 201)
        r = self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "r@example.com", "amount": "300"})
        self.assertEqual(r.status_code, 201)
        # balances
        r = self.client.get("/api/v1/wallet/wallet/")
        self.assertEqual(r.json()["balance"], "700.00")
        # recipient
        c2 = APIClient()
        t2 = c2.post("/api/v1/accounts/login/", {"email": "r@example.com", "password": "TestPass123!"}).json()["token"]
        c2.credentials(HTTP_AUTHORIZATION=f"Token {t2}")
        r = c2.get("/api/v1/wallet/wallet/")
        self.assertEqual(r.json()["balance"], "300.00")

    def test_transfer_insufficient(self):
        r = self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "r@example.com", "amount": "10"})
        self.assertEqual(r.status_code, 400)

    def test_transfer_negative(self):
        r = self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "r@example.com", "amount": "-5"})
        self.assertEqual(r.status_code, 400)

    def test_idempotency(self):
        self.client.post("/api/v1/wallet/topup-demo/", {"amount": "1000"})
        key = str(uuid.uuid4())
        r1 = self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "r@example.com", "amount": "100", "idempotency_key": key})
        r2 = self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "r@example.com", "amount": "100", "idempotency_key": key})
        self.assertEqual(r1.json()["reference"], r2.json()["reference"])


class PermissionTests(BaseTestCase):
    def test_normal_user_no_admin(self):
        u = make_user("x@example.com")
        c = APIClient()
        t = c.post("/api/v1/accounts/login/", {"email": "x@example.com", "password": "TestPass123!"}).json()["token"]
        c.credentials(HTTP_AUTHORIZATION=f"Token {t}")
        r = c.get("/admin/")
        self.assertIn(r.status_code, (302, 403, 404))


class LogisticsTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        u = make_user("l@example.com")
        t = self.client.post("/api/v1/accounts/login/", {"email": "l@example.com", "password": "TestPass123!"}).json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {t}")

    def test_create_shipment_and_event(self):
        r = self.client.post("/api/v1/logistics/shipments/", {"name": "Colis", "origin": "Tana", "destination": "Paris", "mode": "aerien"})
        self.assertEqual(r.status_code, 201)
        ref = r.json()["reference"] if "reference" in r.json() else None
        # list to get ref
        r2 = self.client.get("/api/v1/logistics/shipments/")
        data = r2.json()
        items = data.get("results", data)
        ref = items[0]["reference"]
        r3 = self.client.post(f"/api/v1/logistics/shipments/{ref}/events/", {"status": "transit", "location": "Dubai"})
        self.assertEqual(r3.status_code, 201)
        r4 = self.client.get(f"/api/v1/logistics/shipments/{ref}/")
        self.assertEqual(r4.json()["status"], "transit")


class CustomsTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        make_user("c@example.com")
        t = self.client.post("/api/v1/accounts/login/", {"email": "c@example.com", "password": "TestPass123!"}).json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {t}")

    def test_create_case_and_toggle(self):
        r = self.client.post("/api/v1/customs/cases/", {"description": "Marchandise", "origin_country": "Chine", "destination_country": "Madagascar"})
        self.assertEqual(r.status_code, 201)
        data = self.client.get("/api/v1/customs/cases/").json()
        items = data.get("results", data)
        ref = items[0]["reference"]
        d = self.client.get(f"/api/v1/customs/cases/{ref}/").json()
        req_id = d["requirements"][0]["id"]
        r2 = self.client.post(f"/api/v1/customs/cases/{ref}/requirements/{req_id}/toggle/")
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.json()["provided"])


class BlockchainTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        make_user("b2@example.com")
        t = self.client.post("/api/v1/accounts/login/", {"email": "b2@example.com", "password": "TestPass123!"}).json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {t}")

    def test_record_and_verify(self):
        r = self.client.post("/api/v1/blockchain/records/", {"record_type": "document", "payload": "hello"})
        self.assertEqual(r.status_code, 201)
        r2 = self.client.post("/api/v1/blockchain/verify/", {"payload": "hello"})
        self.assertTrue(r2.json()["verified"])

    def test_info(self):
        r = self.client.get("/api/v1/blockchain/info/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("message", r.json())


class PaymentsTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        make_user("p@example.com")
        t = self.client.post("/api/v1/accounts/login/", {"email": "p@example.com", "password": "TestPass123!"}).json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {t}")

    def test_intl_estimate(self):
        r = self.client.post("/api/v1/payments/international/estimate/", {
            "origin_country": "Madagascar", "destination_country": "France",
            "origin_currency": "MGA", "destination_currency": "EUR", "amount": 100000
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()["real_transfers_enabled"])

    def test_mobile_money_info(self):
        r = self.client.get("/api/v1/payments/mobile-money/info/")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()["available"])


class RegisterValidationTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_password_mismatch(self):
        r = self.client.post("/api/v1/accounts/register/", {
            "email": "m1@example.com", "password": "TestPass123!", "password_confirm": "Different123!"
        })
        self.assertEqual(r.status_code, 400)

    def test_password_too_short(self):
        r = self.client.post("/api/v1/accounts/register/", {
            "email": "m2@example.com", "password": "abc", "password_confirm": "abc"
        })
        self.assertEqual(r.status_code, 400)

    def test_duplicate_email(self):
        make_user("m3@example.com")
        r = self.client.post("/api/v1/accounts/register/", {
            "email": "m3@example.com", "password": "TestPass123!", "password_confirm": "TestPass123!"
        })
        self.assertEqual(r.status_code, 400)


class IdempotencyRobustnessTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = make_user("i1@example.com")
        self.u2 = make_user("i2@example.com")
        r = self.client.post("/api/v1/accounts/login/", {"email": "i1@example.com", "password": "TestPass123!"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {r.json()['token']}")
        self.client.post("/api/v1/wallet/topup-demo/", {"amount": "1000"})

    def test_replay_single_row_single_charge(self):
        key = str(uuid.uuid4())
        r1 = self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "i2@example.com", "amount": "400", "idempotency_key": key})
        self.assertEqual(r1.status_code, 201)
        r2 = self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "i2@example.com", "amount": "400", "idempotency_key": key})
        self.assertEqual(r2.status_code, 201)
        self.assertEqual(r1.json()["reference"], r2.json()["reference"])
        self.assertEqual(Transaction.objects.filter(idempotency_key=key).count(), 1)
        self.assertEqual(Wallet.objects.get(user=self.u1).balance, Decimal("600.00"))
        self.assertEqual(Wallet.objects.get(user=self.u2).balance, Decimal("400.00"))

    def test_transfer_then_check_ledger_consistency(self):
        self.client.post("/api/v1/wallet/topup-demo/", {"amount": "500"})
        r = self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "i2@example.com", "amount": "250"})
        self.assertEqual(r.status_code, 201)
        ref = r.json()["reference"]
        tx = Transaction.objects.get(reference=ref)
        entries = LedgerEntry.objects.filter(transaction=tx).order_by("entry_type")
        self.assertEqual(entries.count(), 2)
        debit = entries.filter(entry_type=LedgerEntry.ENTRY_DEBIT).get()
        credit = entries.filter(entry_type=LedgerEntry.ENTRY_CREDIT).get()
        self.assertEqual(debit.balance_after, Wallet.objects.get(user=self.u1).balance)
        self.assertEqual(credit.balance_after, Wallet.objects.get(user=self.u2).balance)

    def test_topup_over_limit(self):
        r = self.client.post("/api/v1/wallet/topup-demo/", {"amount": "2000000"})
        self.assertEqual(r.status_code, 400)

    def test_cannot_transfer_to_self(self):
        r = self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "i1@example.com", "amount": "100"})
        self.assertEqual(r.status_code, 400)


class NotificationTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        self.sender = make_user("n-s@example.com")
        self.recipient = make_user("n-r@example.com")

    def _login(self, email):
        r = self.client.post("/api/v1/accounts/login/", {"email": email, "password": "TestPass123!"})
        token = r.json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_transfer_creates_notification_and_mark_read(self):
        self._login("n-s@example.com")
        self.client.post("/api/v1/wallet/topup-demo/", {"amount": "1000"})
        self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "n-r@example.com", "amount": "150"})

        self._login("n-r@example.com")
        r = self.client.get("/api/v1/notifications/")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        items = data.get("results", data)
        self.assertTrue(items)
        nid = items[0]["id"]
        self.assertFalse(items[0]["is_read"])

        # marquer une seule notification comme lue
        r2 = self.client.post(f"/api/v1/notifications/{nid}/read/")
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.json()["is_read"])
        self.assertTrue(Notification.objects.get(pk=nid).is_read)

        # tout marquer comme lu
        r3 = self.client.post("/api/v1/notifications/read-all/")
        self.assertEqual(r3.status_code, 200)
        unread = Notification.objects.filter(user=self.recipient, is_read=False).count()
        self.assertEqual(unread, 0)

    def test_cannot_read_foreign_notification(self):
        self._login("n-s@example.com")
        n = Notification.objects.create(user=self.sender, title="Interne", message="test")
        self._login("n-r@example.com")
        r = self.client.post(f"/api/v1/notifications/{n.pk}/read/")
        self.assertEqual(r.status_code, 404)

    def test_list_requires_auth(self):
        r = self.client.get("/api/v1/notifications/")
        self.assertIn(r.status_code, (401, 403))


class ProfileTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        make_user("pr@example.com")
        r = self.client.post("/api/v1/accounts/login/", {"email": "pr@example.com", "password": "TestPass123!"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {r.json()['token']}")

    def test_update_profile_fields(self):
        r = self.client.patch("/api/v1/accounts/me/", {"first_name": "Aina", "phone": "0341234567", "country": "Madagascar"})
        self.assertEqual(r.status_code, 200)
        u = User.objects.get(email="pr@example.com")
        self.assertEqual(u.first_name, "Aina")
        self.assertEqual(u.phone, "0341234567")

    def test_cannot_change_email_via_profile(self):
        r = self.client.patch("/api/v1/accounts/me/", {"email": "hacked@example.com"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(User.objects.filter(email="pr@example.com").exists())
        self.assertFalse(User.objects.filter(email="hacked@example.com").exists())


class LogoutTests(BaseTestCase):
    def test_logout_invalidates_token(self):
        u = make_user("lg@example.com")
        c = APIClient()
        t = c.post("/api/v1/accounts/login/", {"email": "lg@example.com", "password": "TestPass123!"}).json()["token"]
        c.credentials(HTTP_AUTHORIZATION=f"Token {t}")
        self.assertEqual(c.get("/api/v1/accounts/me/").status_code, 200)
        self.assertEqual(c.post("/api/v1/accounts/logout/").status_code, 200)
        # le token est supprimé: l'accès profil échoue ensuite
        r = c.get("/api/v1/accounts/me/")
        self.assertIn(r.status_code, (401, 403))
        # et le token obsolète ne fonctionne plus depuis un client séparé
        c2 = APIClient()
        c2.credentials(HTTP_AUTHORIZATION=f"Token {t}")
        self.assertIn(c2.get("/api/v1/accounts/me/").status_code, (401, 403))
        self.assertTrue(u.email)


from audit.models import AuditLog
from payments.models import ExchangeRate
from django.test import TransactionTestCase


class RootIndexTests(BaseTestCase):
    def test_index_lists_endpoints(self):
        r = self.client.get("/api/")
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d["status"], "ok")
        self.assertIn("wallet", d["endpoints"])
        self.assertIn("notifications", d["endpoints"])


class PaymentsRatesTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        make_user("pr2@example.com")
        t = self.client.post("/api/v1/accounts/login/", {"email": "pr2@example.com", "password": "TestPass123!"}).json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {t}")
        ExchangeRate.objects.create(base="MGA", target="EUR", rate=Decimal("0.000200"), source="test")

    def test_rates_list(self):
        r = self.client.get("/api/v1/payments/rates/")
        self.assertEqual(r.status_code, 200)
        items = r.json().get("results", r.json())
        pair = [x for x in items if x["base"] == "MGA" and x["target"] == "EUR"]
        self.assertTrue(pair)
        self.assertEqual(pair[0]["source"], "test")

    def test_estimate_uses_stored_rate_and_subtracts_fee(self):
        r = self.client.post("/api/v1/payments/international/estimate/", {
            "origin_country": "Madagascar", "destination_country": "France",
            "origin_currency": "MGA", "destination_currency": "EUR", "amount": 1000000,
        })
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d["rate"], "0.000200")
        self.assertEqual(d["rate_source"], "test")
        # frais = 2% (20000) ; reçu = (montant - frais) * taux = 196.00
        self.assertEqual(d["estimated_fee"], "20000.00")
        self.assertEqual(d["estimated_receive"], "196.00")
        self.assertTrue(d["reference"].startswith("INT-"))
        self.assertFalse(d["real_transfers_enabled"])

    def test_estimate_without_rate_uses_demo_fallback(self):
        r = self.client.post("/api/v1/payments/international/estimate/", {
            "origin_country": "Madagascar", "destination_country": "Japon",
            "origin_currency": "MGA", "destination_currency": "JPY", "amount": 500000,
        })
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertIn("démonstration", d["rate_source"])

    def test_estimate_invalid_amounts(self):
        for amount in ("abc", "-100", None):
            payload = {
                "origin_country": "Madagascar", "destination_country": "France",
                "origin_currency": "MGA", "destination_currency": "EUR", "amount": amount,
            }
            r = self.client.post("/api/v1/payments/international/estimate/", payload, format="json")
            self.assertEqual(r.status_code, 400, f"amount={amount}")

    def test_connectors_list(self):
        r = self.client.get("/api/v1/payments/connectors/")
        self.assertEqual(r.status_code, 200)


class LogisticsTimelineTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        make_user("l2@example.com")
        t = self.client.post("/api/v1/accounts/login/", {"email": "l2@example.com", "password": "TestPass123!"}).json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {t}")
        r = self.client.post("/api/v1/logistics/shipments/", {"name": "Colis 2", "origin": "Toamasina", "destination": "Paris", "mode": "maritime"})
        self.assertEqual(r.status_code, 201)
        data = self.client.get("/api/v1/logistics/shipments/").json()
        items = data.get("results", data)
        self.ref = items[0]["reference"]

    def test_two_events_kept_and_status_tracks_latest(self):
        r1 = self.client.post(f"/api/v1/logistics/shipments/{self.ref}/events/", {"status": "attente_depart", "location": "Toamasina"})
        self.assertEqual(r1.status_code, 201)
        r2 = self.client.post(f"/api/v1/logistics/shipments/{self.ref}/events/", {"status": "transit", "location": "Suez"})
        self.assertEqual(r2.status_code, 201)
        d = self.client.get(f"/api/v1/logistics/shipments/{self.ref}/").json()
        self.assertEqual(d["status"], "transit")
        events = d.get("events", [])
        self.assertGreaterEqual(len(events), 2)

    def test_shipment_requires_auth(self):
        c = APIClient()
        r = c.get(f"/api/v1/logistics/shipments/{self.ref}/")
        self.assertIn(r.status_code, (401, 403))

    def test_unknown_shipment_404(self):
        r = self.client.get("/api/v1/logistics/shipments/INCONNUE/")
        self.assertEqual(r.status_code, 404)


class TransactionDetailAccessTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        self.sender = make_user("td-s@example.com")
        self.recipient = make_user("td-r@example.com")
        self.third = make_user("td-x@example.com")

    def _login(self, email):
        r = self.client.post("/api/v1/accounts/login/", {"email": email, "password": "TestPass123!"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {r.json()['token']}")

    def test_parties_can_view_stranger_cannot_and_404_unknown(self):
        self._login("td-s@example.com")
        self.client.post("/api/v1/wallet/topup-demo/", {"amount": "1000"})
        ref = self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "td-r@example.com", "amount": "250"}).json()["reference"]
        path = f"/api/v1/wallet/transactions/{ref}/"

        self._login("td-s@example.com")
        self.assertEqual(self.client.get(path).status_code, 200)
        self._login("td-r@example.com")
        self.assertEqual(self.client.get(path).status_code, 200)
        self._login("td-x@example.com")
        self.assertEqual(self.client.get(path).status_code, 403)

        r = self.client.get("/api/v1/wallet/transactions/inexistant/")
        self.assertEqual(r.status_code, 404)


class AuditTrailTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        make_user("au@example.com")
        make_user("au-r@example.com")
        t = self.client.post("/api/v1/accounts/login/", {"email": "au@example.com", "password": "TestPass123!"}).json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {t}")

    def test_topup_and_transfer_write_audit_log(self):
        self.client.post("/api/v1/wallet/topup-demo/", {"amount": "1000"})
        r = self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "au-r@example.com", "amount": "100"})
        self.assertEqual(r.status_code, 201)
        actions = set(AuditLog.objects.values_list("action", flat=True))
        self.assertIn("wallet.topup_demo", actions)
        self.assertIn("transfer.completed", actions)
        transfer_log = AuditLog.objects.filter(action="transfer.completed").first()
        self.assertTrue(transfer_log)
        self.assertEqual(transfer_log.metadata.get("amount"), "100")
        self.assertEqual(transfer_log.metadata.get("recipient"), "au-r@example.com")


class BlockchainVerifyNegativeTests(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
        make_user("bn2@example.com")
        t = self.client.post("/api/v1/accounts/login/", {"email": "bn2@example.com", "password": "TestPass123!"}).json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {t}")

    def test_verify_unknown_payload_fails(self):
        r = self.client.post("/api/v1/blockchain/verify/", {"payload": "jamais enregistre"})
        self.assertEqual(r.status_code, 404)
        self.assertFalse(r.json()["verified"])


class BaseTransactionTestCase(TransactionTestCase):
    """TransactionTestCase avec hachage de mot de passe rapide (pour les tests de concurrence)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.enterClassContext(override_settings(PASSWORD_HASHERS=FAST_PASSWORD_HASHERS))
        cls.enterClassContext(override_settings(REST_FRAMEWORK={
            "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication", "rest_framework.authentication.TokenAuthentication"),
            "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
            "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
            "PAGE_SIZE": 20,
            "DEFAULT_THROTTLE_RATES": FAST_THROTTLE_RATES,
        }))


class TransferConcurrencyTests(BaseTransactionTestCase):
    """Deux threads simultanés avec la même clé d'idempotence : une seule écriture."""

    def setUp(self):
        self.sender = make_user("cc-s@example.com")
        self.recipient = make_user("cc-r@example.com")
        from wallet.services import topup_demo
        topup_demo(self.sender, Decimal("10000"))

    def _race(self, results, i, key):
        import time
        from django.db import connection, OperationalError
        from wallet.services import transfer_funds
        try:
            # SQLite en mode concurrent peut lever "database table is locked"
            # (pas de verrous de ligne). Le client doit donc reprendre sa
            # tentative ; avec PostgreSQL transfer_funds bloque proprement
            # via select_for_update et la reprise n'est jamais déclenchée.
            for attempt in range(6):
                try:
                    tx = transfer_funds(self.sender, self.recipient.email, Decimal("100"), f"race {i}", key)
                    results.append(str(tx.reference))
                    return
                except OperationalError as e:
                    results_append_err = e
                    time.sleep(0.05 * (attempt + 1))
            results.append(f"ERR:{type(results_append_err).__name__}: {results_append_err}")
        except Exception as e:  # pragma: no cover - diagnostique en cas d'échec
            results.append(f"ERR:{type(e).__name__}: {e}")
        finally:
            connection.close()

    def test_concurrent_same_key_charges_once(self):
        import threading
        key = str(uuid.uuid4())
        results = []
        threads = [threading.Thread(target=self._race, args=(results, i, key)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(60)

        errs = [r for r in results if isinstance(r, str) and r.startswith("ERR:")]
        refs = {str(r) for r in results if not (isinstance(r, str) and r.startswith("ERR:"))}
        self.assertFalse(errs, f"erreurs pendant la course: {errs}")
        self.assertTrue(refs, "au moins un thread doit réussir")
        self.assertEqual(len(refs), 1, "toutes les réponses doivent partager la même référence")
        self.assertEqual(Transaction.objects.filter(idempotency_key=key).count(), 1, "une seule transaction")
        self.assertEqual(Wallet.objects.get(user=self.sender).balance, Decimal("9900.00"), "débité une seule fois")
        self.assertEqual(Wallet.objects.get(user=self.recipient).balance, Decimal("100.00"), "crédité une seule fois")


class IdempotencyScopingTests(BaseTestCase):
    """La clé d'idempotence est scopée au propriétaire (audit ChatGPT)."""

    def setUp(self):
        self.c1 = APIClient()
        self.c2 = APIClient()
        make_user("scope-a@example.com")
        make_user("scope-b@example.com")
        t1 = self.c1.post("/api/v1/accounts/login/", {"email": "scope-a@example.com", "password": "TestPass123!"}).json()["token"]
        t2 = self.c2.post("/api/v1/accounts/login/", {"email": "scope-b@example.com", "password": "TestPass123!"}).json()["token"]
        self.c1.credentials(HTTP_AUTHORIZATION=f"Token {t1}")
        self.c2.credentials(HTTP_AUTHORIZATION=f"Token {t2}")
        self.c1.post("/api/v1/wallet/topup-demo/", {"amount": "1000"})
        self.c2.post("/api/v1/wallet/topup-demo/", {"amount": "1000"})

    def test_same_key_different_users_no_collision(self):
        key = str(uuid.uuid4())
        # User A transfers with key
        r1 = self.c1.post("/api/v1/wallet/transfer/", {"recipient_email": "scope-b@example.com", "amount": "100", "idempotency_key": key})
        self.assertEqual(r1.status_code, 201)
        # User B uses the SAME key — should create a NEW transaction (not collide)
        r2 = self.c2.post("/api/v1/wallet/transfer/", {"recipient_email": "scope-a@example.com", "amount": "50", "idempotency_key": key})
        self.assertEqual(r2.status_code, 201)
        self.assertNotEqual(r1.json()["reference"], r2.json()["reference"])
        # Two distinct transactions
        self.assertEqual(Transaction.objects.filter(idempotency_key=key).count(), 2)

    def test_replay_same_user_returns_same_tx(self):
        key = str(uuid.uuid4())
        r1 = self.c1.post("/api/v1/wallet/transfer/", {"recipient_email": "scope-b@example.com", "amount": "100", "idempotency_key": key})
        r2 = self.c1.post("/api/v1/wallet/transfer/", {"recipient_email": "scope-b@example.com", "amount": "100", "idempotency_key": key})
        self.assertEqual(r1.json()["reference"], r2.json()["reference"])
        self.assertEqual(Transaction.objects.filter(idempotency_key=key, sender__email="scope-a@example.com").count(), 1)


class BlockchainRefreshTests(BaseTestCase):
    """Endpoint de rafraîchissement des statuts blockchain."""

    def setUp(self):
        self.client = APIClient()
        make_user("br@example.com")
        t = self.client.post("/api/v1/accounts/login/", {"email": "br@example.com", "password": "TestPass123!"}).json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {t}")

    def test_refresh_returns_counts(self):
        # Create a record first
        r = self.client.post("/api/v1/blockchain/records/", {"record_type": "document", "payload": "test-refresh"})
        self.assertEqual(r.status_code, 201)
        # Refresh (no RPC configured → no updates, but endpoint works)
        r2 = self.client.post("/api/v1/blockchain/refresh/", {})
        self.assertEqual(r2.status_code, 200)
        self.assertIn("updated", r2.json())
        self.assertIn("checked", r2.json())

    def test_refresh_requires_auth(self):
        c = APIClient()
        r = c.post("/api/v1/blockchain/refresh/", {})
        self.assertIn(r.status_code, (401, 403))


class GuestAccessTests(BaseTestCase):
    """Compte invité de démonstration (aucun mot de passe demandé)."""

    def setUp(self):
        self.client = APIClient()

    def test_guest_creates_demo_account_with_balance(self):
        r = self.client.post("/api/v1/accounts/guest/", {"language": "mg"})
        self.assertEqual(r.status_code, 201)
        d = r.json()
        self.assertIn("token", d)
        email = d["user"]["email"]
        self.assertTrue(email.startswith("invite."))
        self.assertEqual(User.objects.get(email=email).preferred_language, "mg")
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f"Token {d['token']}")
        w = c.get("/api/v1/wallet/wallet/").json()
        self.assertEqual(w["balance"], "50000.00")

    def test_guest_language_fallback(self):
        r = self.client.post("/api/v1/accounts/guest/", {"language": "xx"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["user"]["preferred_language"], "fr")


class TransactionFingerprintTests(BaseTestCase):
    """Chaque opération clôturée laisse une empreinte blockchain de test."""

    def setUp(self):
        self.client = APIClient()
        make_user("fp-r@example.com")
        make_user("fresh@example.com")
        t = self.client.post("/api/v1/accounts/login/", {"email": "fresh@example.com", "password": "TestPass123!"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {t.json()['token']}")

    def test_topup_creates_record_and_verify_by_reference(self):
        from blockchain.models import BlockchainRecord
        r = self.client.post("/api/v1/wallet/topup-demo/", {"amount": "1000"})
        self.assertEqual(r.status_code, 201)
        ref = r.json()["reference"]
        rec = BlockchainRecord.objects.filter(metadata__reference=ref, record_type="transaction")
        self.assertTrue(rec.exists())
        r2 = self.client.post("/api/v1/blockchain/verify/", {"reference": ref})
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.json()["verified"])

    def test_transfer_creates_record(self):
        from blockchain.models import BlockchainRecord
        self.client.post("/api/v1/wallet/topup-demo/", {"amount": "1000"})
        r = self.client.post("/api/v1/wallet/transfer/", {"recipient_email": "fp-r@example.com", "amount": "100"})
        self.assertEqual(r.status_code, 201)
        ref = r.json()["reference"]
        self.assertTrue(BlockchainRecord.objects.filter(metadata__reference=ref).exists())


class ApiIndexV1Tests(BaseTestCase):
    def test_index_v1(self):
        r = self.client.get("/api/v1/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")
