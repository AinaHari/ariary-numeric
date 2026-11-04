import flet as ft

from mobile.components.common import *
from mobile.services.api import ApiClient


def build_register(page, state, navigate):
    email = text_field("Adresse e-mail")
    first = text_field("Prénom")
    last = text_field("Nom")
    phone = text_field("Téléphone")
    password = text_field("Mot de passe", password=True)
    password2 = text_field("Confirmer le mot de passe", password=True)

    def do_register(e):
        if password.value != password2.value:
            snackbar(page, "Les mots de passe ne correspondent pas.", error=True)
            return
        r = state["api"].register(email.value.strip(), password.value, password2.value,
                                  first_name=first.value, last_name=last.value, phone=phone.value)
        if r is None:
            snackbar(page, "Serveur inaccessible.", error=True)
            return
        if r.status_code not in (200, 201):
            try:
                msg = r.json()
                if isinstance(msg, dict):
                    msg = "; ".join(f"{k}: {v}" for k, v in msg.items())
            except Exception:
                msg = "Inscription échouée."
            snackbar(page, str(msg), error=True)
            return
        data = r.json()
        from mobile.screens.login import _on_auth_success
        _on_auth_success(page, state, data)
        snackbar(page, "Compte créé.")
        navigate("dashboard")

    def go_login(e):
        navigate("login")

    return ft.View(route="/register",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        title("Créer un compte"),
                        card(ft.Column([
                            email, first, last, phone, password, password2,
                            button("S'inscrire", do_register, width=300),
                        ])),
                        ft.TextButton("Déjà un compte ? Se connecter", on_click=go_login),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
            )
        ],
    )
