import flet as ft

from mobile.components.common import *


def build_payments(page, state, navigate):
    info = ft.Text("Paiements mobile money réels non disponibles dans cette version")
    rates = ft.Column()
    intl_result = ft.Text("")
    intl_list = ft.Column()

    origin_country = text_field("Pays d'origine", )
    origin_country.value = "Madagascar"
    destination_country = text_field("Pays de destination")
    origin_currency = text_field("Devise origine")
    origin_currency.value = "MGA"
    destination_currency = text_field("Devise destination")
    destination_currency.value = "EUR"
    amount = text_field("Montant", keyboard=ft.KeyboardType.NUMBER)

    def refresh_rates():
        rates.controls.clear()
        r = state["api"].rates()
        if r and r.status_code == 200:
            for rt in as_list(r):
                rates.controls.append(ft.Text(f"{rt['base']}/{rt['target']} = {rt['rate']} ({rt['source']})"))
        if not rates.controls:
            rates.controls.append(ft.Text("Aucun taux."))
        # infos mobile money
        r2 = state["api"].mobile_money_info()
        if r2 and r2.status_code == 200:
            d2 = r2.json()
            info.value = f"{d2.get('message','')} (disponible: {d2.get('available')})"
        page.update()

    def refresh_intl():
        intl_list.controls.clear()
        r = state["api"].intl_list()
        if r and r.status_code == 200:
            for it in as_list(r):
                intl_list.controls.append(ft.Text(f"{it['reference']} — {it['amount']} {it['origin_currency']} → {it['estimated_receive']} {it['destination_currency']} ({it['status']})"))
        if not intl_list.controls:
            intl_list.controls.append(ft.Text("Aucune estimation."))
        page.update()

    def estimate(e):
        try:
            val = float(amount.value)
        except Exception:
            snackbar(page, "Montant invalide.", error=True)
            return
        payload = {
            "origin_country": origin_country.value, "destination_country": destination_country.value,
            "origin_currency": origin_currency.value, "destination_currency": destination_currency.value,
            "amount": val,
        }
        r = state["api"].intl_estimate(payload)
        if r and r.status_code in (200, 201):
            d = r.json()
            intl_result.value = (f"Réf: {d['reference']}\nTaux: {d['rate']} ({d['rate_source']})\n"
                                 f"Frais estimés: {d['estimated_fee']} {d['origin_currency']}\n"
                                 f"Montant estimé reçu: {d['estimated_receive']} {d['destination_currency']}\n"
                                 f"Statut: {d['status']}\n{d['note']}")
            refresh_intl()
        else:
            intl_result.value = error_message(r)
        page.update()

    refresh_rates()
    refresh_intl()

    return ft.View(route="/payments",
        appbar=ft.AppBar(title=ft.Text("Paiements internationaux", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("dashboard"), icon_color="white")),
        controls=[ft.Container(content=ft.Column([
            card(ft.Text(info.value)),
            ft.Text("Taux de change", weight=ft.FontWeight.BOLD), rates,
            ft.Text("Estimation de transfert international", weight=ft.FontWeight.BOLD),
            origin_country, destination_country, origin_currency, destination_currency, amount,
            button("Estimer", estimate),
            card(intl_result),
            ft.Text("Mes estimations", weight=ft.FontWeight.BOLD), intl_list,
        ], scroll=ft.ScrollMode.AUTO), padding=16)],
    )
