import flet as ft

from mobile.components.common import *


def build_history(page, state, navigate):
    tx_list = ft.Column(scroll=ft.ScrollMode.AUTO)

    def refresh():
        tx_list.controls.clear()
        r = state["api"].transactions()
        if r and r.status_code == 200:
            for t in as_list(r):
                tx_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{t['amount']} {t['currency']} — {t['kind']}"),
                        subtitle=ft.Text(f"{t['status']} • {t['created_at'][:19]}"),
                        trailing=ft.Text(str(t['reference'])[:8]),
                        on_click=lambda e, ref=t['reference']: (state.update({"selected_tx": ref}), navigate("txdetail")),
                    )
                )
        if not tx_list.controls:
            tx_list.controls.append(ft.Text("Aucune transaction."))
        page.update()

    refresh()

    return ft.View(route="/history",
        appbar=ft.AppBar(title=ft.Text("Historique", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("dashboard"), icon_color="white")),
        controls=[ft.Container(content=tx_list, padding=16)],
    )
