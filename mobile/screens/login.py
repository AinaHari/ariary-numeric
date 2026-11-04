import flet as ft

from mobile.components.common import *
from mobile.services.api import ApiClient


def _on_auth_success(page, state, data):
    token = data.get("token")
    user = data.get("user")
    if token:
        state["api"].set_token(token)
        store = state.get("token_store")
        if store:
            store.set(token)
    state["user"] = user


def build_login(page, state, navigate):
    email = text_field("Adresse e-mail")
    password = text_field("Mot de passe", password=True)

    def do_login(e):
        r = state["api"].login(email.value.strip(), password.value)
        if r is None:
            snackbar(page, "Serveur inaccessible.", error=True)
            return
        if r.status_code != 200:
            try:
                msg = r.json().get("detail", "Connexion échouée.")
            except Exception:
                msg = "Connexion échouée."
            snackbar(page, msg, error=True)
            return
        _on_auth_success(page, state, r.json())
        snackbar(page, "Connexion réussie.")
        navigate("dashboard")

    def do_guest(e):
        # Type client rapide qui ne demande pas d'inscription.
        r = state["api"].request("POST", "/api/v1/accounts/guest/", json={"language": "fr"})
        if r is None or r.status_code not in (200, 201):
            snackbar(page, "Impossible de créer un compte invité.", error=True)
            return
        _on_auth_success(page, state, r.json())
        snackbar(page, "Compte invité créé (50 000 MGA de démonstration).")
        navigate("dashboard")

    def go_register(e):
        navigate("register")

    return ft.View(route="/login",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("ARIARY NUMERIC", size=28, weight=ft.FontWeight.BOLD, color=PRIMARY),
                        ft.Text("Portefeuille numérique de démonstration", size=13, color="#555"),
                        ft.Container(height=20),
                        card(ft.Column([email, password, button("Se connecter", do_login, width=300)])),
                        ft.Container(height=10),
                        button("Essayer sans compte (invité)", do_guest, primary=False, width=300),
                        ft.TextButton("Créer un compte", on_click=go_register),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                alignment=ft.Alignment.CENTER,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
    )
