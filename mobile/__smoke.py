"""Smoke test : instancie chaque écran avec un faux Page pour valider
la construction des vues (aucun crash d'API Flet)."""

import asyncio
import sys
import traceback

sys.path.insert(0, ".")

import flet as ft

from mobile.components.common import BG, PRIMARY


class FakePage:
    """Page minimale compatible avec les écrans existants."""

    def __init__(self, route="/dashboard"):
        self.route = route
        self.bgcolor = BG
        self.title = "Ariary Numeric"
        self.views = []
        self.overlay = []
        self.data = {}
        self.services = []
        self.theme = None
        self.on_route_change = None
        self.on_view_pop = None
        self._snackbars = []

    # API utilisées par les écrans.
    def navigate(self, path, **kwargs):
        self.route = path
        if self.on_route_change:
            self.on_route_change()

    def show_dialog(self, dlg):
        self.overlay.append(dlg)

    def update(self, *_a, **_kw):
        pass


def make_fake_api():
    class FakeResp:
        def __init__(self, status_code=200, data=None):
            self.status_code = status_code
            self._data = data if data is not None else {"balance": "0", "currency": "MGA", "results": []}

        def json(self):
            return self._data

    class A:
        token = "demo-token"

        def set_token(self, v):
            self.token = v

        def clear(self):
            self.token = None

        def request(self, *_a, **_kw):
            return FakeResp()

        def logout(self):
            return FakeResp()

        def profile(self):
            return FakeResp(data={"email": "demo@example.com", "created_at": "2025-01-01T00:00:00Z", "first_name": "Démo"})

        def wallet(self):
            return FakeResp(data={"balance": "0", "currency": "MGA"})

        def transactions(self):
            return FakeResp(data={"results": []})

        def transaction_detail(self, ref):
            return FakeResp(data={"reference": ref, "amount": "0", "currency": "MGA", "kind": "transfer"})

        def notifications(self):
            return FakeResp(data={"results": []})

        def shipments(self):
            return FakeResp(data={"results": []})

        def shipment_detail(self, ref):
            return FakeResp(data={"reference": ref, "name": "—", "origin": "—", "destination": "—", "status": "preparation", "mode": "maritime", "events": []})

        def customs_cases(self):
            return FakeResp(data={"results": []})

        def customs_detail(self, ref):
            return FakeResp(data={"reference": ref, "description": "—", "origin_country": "—", "destination_country": "—", "status": "cree", "requirements": [], "events": []})

        def blockchain_info(self):
            return FakeResp(data={"network": "sepolia", "chain_id": 11155111, "rpc_configured": False, "message": "Blockchain de test non configurée"})

        def blockchain_records(self):
            return FakeResp(data={"results": []})

        def rates(self):
            return FakeResp(data={"results": []})

        def intl_list(self):
            return FakeResp(data={"results": []})

        def mobile_money_info(self):
            return FakeResp(data={"message": "Paiements mobile money réels non disponibles", "available": False})

        # Méthodes écrivaines : renvoient une réponse neutre.
        def __getattr__(self, name):
            return lambda *a, **kw: FakeResp(status_code=200)

    return A()


def check(name, builder):
    page = FakePage(route="/dashboard")
    state = {
        "api": make_fake_api(),
        "user": {"email": "demo@example.com", "first_name": "Démo"},
    }
    try:
        view = builder(page, state, lambda x: page.navigate("/" + x))
    except Exception:
        print(f"[FAIL] {name}")
        traceback.print_exc()
        return False
    if view is None or not getattr(view, "controls", None):
        print(f"[FAIL] {name}: vue vide")
        return False
    print(f"[OK]   {name}")
    return True


def main():
    from mobile.screens import (
        login, register, dashboard, topup, wallet, txdetail, transfer,
        history, qr, qrconfirm, shipments, shipment_create, shipment_detail,
        customs, customs_create, customs_detail, blockchain, payments,
        notifications, profile,
    )

    builders = {
        "login": login.build_login,
        "register": register.build_register,
        "dashboard": dashboard.build_dashboard,
        "topup": topup.build_topup,
        "wallet": wallet.build_wallet,
        "txdetail": txdetail.build_txdetail,
        "transfer": transfer.build_transfer,
        "history": history.build_history,
        "qr": qr.build_qr,
        "qrconfirm": qrconfirm.build_qrconfirm,
        "shipments": shipments.build_shipments,
        "shipmentcreate": shipment_create.build_shipment_create,
        "shipmentdetail": shipment_detail.build_shipment_detail,
        "customs": customs.build_customs,
        "customscreate": customs_create.build_customs_create,
        "customsdetail": customs_detail.build_customs_detail,
        "blockchain": blockchain.build_blockchain,
        "payments": payments.build_payments,
        "notifications": notifications.build_notifications,
        "profile": profile.build_profile,
    }
    ok = 0
    for name, b in builders.items():
        if check(name, b):
            ok += 1
    print(f"\n{ok}/{len(builders)} écrans construits sans erreur.")
    return 0 if ok == len(builders) else 1


if __name__ == "__main__":
    sys.exit(main())
