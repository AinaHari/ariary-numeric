import flet as ft

from mobile.components.common import *


def build_customs_create(page, state, navigate):
    desc = text_field("Description de la marchandise")
    origin = text_field("Pays d'origine")
    destination = text_field("Pays de destination")
    mode = ft.Dropdown(label="Mode", options=[ft.dropdown.Option("maritime", "Maritime"), ft.dropdown.Option("aerien", "Aérien"), ft.dropdown.Option("terrestre", "Terrestre")], value="maritime")

    def do_create(e):
        payload = {"description": desc.value, "origin_country": origin.value, "destination_country": destination.value, "mode": mode.value}
        r = state["api"].create_customs_case(payload)
        if r and r.status_code in (200, 201):
            snackbar(page, "Dossier créé.")
            navigate("customs")
        else:
            snackbar(page, error_message(r), error=True)

    return ft.View(route="/customscreate",
        appbar=ft.AppBar(title=ft.Text("Nouveau dossier douane", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("customs"), icon_color="white")),
        controls=[ft.Container(content=card(ft.Column([desc, origin, destination, mode, button("Créer", do_create)])), padding=16)],
    )
