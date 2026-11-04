import flet as ft

from mobile.components.common import *


def build_shipments(page, state, navigate):
    lst = ft.Column(scroll=ft.ScrollMode.AUTO)

    def refresh():
        lst.controls.clear()
        r = state["api"].shipments()
        if r and r.status_code == 200:
            for s in as_list(r):
                lst.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{s['reference']} — {s['name']}"),
                        subtitle=ft.Text(f"{s['origin']} → {s['destination']} • {s['status']}"),
                        on_click=lambda e, ref=s['reference']: (state.update({"selected_shipment": ref}), navigate("shipmentdetail")),
                    )
                )
        if not lst.controls:
            lst.controls.append(ft.Text("Aucune expédition."))
        page.update()

    def new_shipment(e):
        navigate("shipmentcreate")

    refresh()

    return ft.View(route="/shipments",
        appbar=ft.AppBar(title=ft.Text("Expéditions", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("dashboard"), icon_color="white")),
        controls=[ft.Container(content=ft.Column([button("Nouvelle expédition", new_shipment), lst]), padding=16)],
    )
