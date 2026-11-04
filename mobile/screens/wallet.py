import flet as ft

from mobile.components.common import *


def build_wallet(page, state, navigate):
    info = ft.Text("Chargement...")
    tx_list = ft.Column(scroll=ft.ScrollMode.AUTO)

    def refresh(e=None):
        r = state["api"].wallet()
        if r and r.status_code == 200:
            d = r.json()
            info.value = f"Solde : {d['balance']} {d['currency']}\nPortefeuille de démonstration — aucun argent réel"
        else:
            info.value = "Indisponible"
        r2 = state["api"].transactions()
        tx_list.controls.clear()
        if r2 and r2.status_code == 200:
            for t in as_list(r2)[:10]:
                tx_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{t['amount']} {t['currency']} — {t['kind']}"),
                        subtitle=ft.Text(f"{t['status']} • {t['created_at'][:19]}"),
                        trailing=ft.Text(str(t['reference'])[:8]),
                        on_click=lambda e, ref=t['reference']: (state.update({"selected_tx": ref}), navigate("txdetail")),
                    )
                )
        page.update()

    refresh()

    return ft.View(route="/wallet",
        appbar=ft.AppBar(title=ft.Text("Portefeuille", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("dashboard"), icon_color="white")),
        controls=[
            ft.Container(content=ft.Column([card(info), ft.Text("Dernières opérations", weight=ft.FontWeight.BOLD), tx_list],
                                          scroll=ft.ScrollMode.AUTO), padding=16)
        ],
    )
