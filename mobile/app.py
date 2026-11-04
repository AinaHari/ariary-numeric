import asyncio
import flet as ft

from mobile.components.common import *
from mobile.services.api import ApiClient
from mobile.services.session import TokenStore

from mobile.screens.login import build_login
from mobile.screens.register import build_register
from mobile.screens.dashboard import build_dashboard
from mobile.screens.topup import build_topup
from mobile.screens.wallet import build_wallet
from mobile.screens.txdetail import build_txdetail
from mobile.screens.transfer import build_transfer
from mobile.screens.history import build_history
from mobile.screens.qr import build_qr
from mobile.screens.qrconfirm import build_qrconfirm
from mobile.screens.shipments import build_shipments
from mobile.screens.shipment_create import build_shipment_create
from mobile.screens.shipment_detail import build_shipment_detail
from mobile.screens.customs import build_customs
from mobile.screens.customs_create import build_customs_create
from mobile.screens.customs_detail import build_customs_detail
from mobile.screens.blockchain import build_blockchain
from mobile.screens.payments import build_payments
from mobile.screens.notifications import build_notifications
from mobile.screens.profile import build_profile

PUBLIC_ROUTES = ("login", "register")

BUILDERS = {
    "login": build_login,
    "register": build_register,
    "dashboard": build_dashboard,
    "topup": build_topup,
    "wallet": build_wallet,
    "txdetail": build_txdetail,
    "transfer": build_transfer,
    "history": build_history,
    "qr": build_qr,
    "qrconfirm": build_qrconfirm,
    "shipments": build_shipments,
    "shipmentcreate": build_shipment_create,
    "shipmentdetail": build_shipment_detail,
    "customs": build_customs,
    "customscreate": build_customs_create,
    "customsdetail": build_customs_detail,
    "blockchain": build_blockchain,
    "payments": build_payments,
    "notifications": build_notifications,
    "profile": build_profile,
}


def make_navigate(page, state, token_store):
    def navigate(name):
        if name == "logout":
            try:
                state["api"].logout()
            except Exception:
                pass
            state["api"].clear()
            state["user"] = None
            token_store.remove()
            page.navigate("/login")
            return
        if name not in BUILDERS:
            name = "dashboard"
        page.navigate("/" + name)

    return navigate


def main(page: ft.Page):
    page.title = "Ariary Numeric"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = BG
    page.padding = 0
    page.theme = ft.Theme(
        color_scheme_seed=PRIMARY,
        font_family="Roboto",
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    token_store = TokenStore()
    token_store.attach(page)
    api = ApiClient()
    state = {"api": api, "user": None, "token_store": token_store}
    page.data = state

    navigate = make_navigate(page, state, token_store)

    def show_route(route):
        name = (route or "/").strip("/") or "login"
        if name not in BUILDERS:
            name = "dashboard" if api.token else "login"
        if name not in PUBLIC_ROUTES and not api.token:
            page.navigate("/login")
            return
        if name in PUBLIC_ROUTES and api.token:
            page.navigate("/dashboard")
            return
        try:
            view = BUILDERS[name](page, state, navigate)
        except Exception as ex:  # jamais d'écran noir
            view = ft.View(
                "/" + name,
                appbar=app_bar("Erreur"),
                controls=[
                    ft.Container(
                        padding=16,
                        content=card(
                            ft.Column(
                                [
                                    ft.Text("Cet écran n'a pas pu s'afficher.", weight=ft.FontWeight.BOLD),
                                    ft.Text(str(ex), size=12, color="#666"),
                                    button("Retour au tableau de bord", lambda e: page.navigate("/dashboard")),
                                ]
                            )
                        ),
                    )
                ],
            )
        page.views.clear()
        page.views.append(view)
        page.update()

    def on_route_change(e=None):
        show_route(getattr(page, "route", "/") or "/")

    page.on_route_change = on_route_change

    def enforce_session(e=None):
        if not api.token and page.route not in ("/login", "/register", "/"):
            page.navigate("/login")

    page.on_view_pop = lambda e: page.navigate("/dashboard") if api.token else page.navigate("/login")

    async def bootstrap():
        # Attendre l'hydratation des préférences partagées.
        for _ in range(20):
            if token_store.value:
                break
            await asyncio.sleep(0.05)
        if token_store.value:
            api.set_token(token_store.value)
            r = api.profile()
            if r is not None and r.status_code == 200:
                state["user"] = r.json()
                page.navigate("/dashboard")
                return
            api.clear()
            token_store.remove()
        page.navigate("/login")

    asyncio.create_task(bootstrap())


def start():
    ft.run(main)


if __name__ == "__main__":
    start()
