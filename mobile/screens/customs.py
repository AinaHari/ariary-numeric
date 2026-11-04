import flet as ft

from mobile.components.common import *


def build_customs(page, state, navigate):
    lst = ft.Column(scroll=ft.ScrollMode.AUTO)

    def refresh():
        lst.controls.clear()
        r = state["api"].customs_cases()
        if r and r.status_code == 200:
            for c in as_list(r):
                lst.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{c['reference']} — {c['description']}"),
                        subtitle=ft.Text(f"{c['origin_country']} → {c['destination_country']} • {c['status']}"),
                        on_click=lambda e, ref=c['reference']: (state.update({"selected_customs": ref}), navigate("customsdetail")),
                    )
                )
        if not lst.controls:
            lst.controls.append(ft.Text("Aucun dossier."))
        page.update()

    def new_case(e):
        navigate("customscreate")

    refresh()

    return ft.View(route="/customs",
        appbar=ft.AppBar(title=ft.Text("Transit & douane", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("dashboard"), icon_color="white")),
        controls=[ft.Container(content=ft.Column([button("Nouveau dossier", new_case), lst]), padding=16)],
    )
