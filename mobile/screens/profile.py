import flet as ft

from mobile.components.common import *


def build_profile(page, state, navigate):
    info = ft.Text("Chargement...")
    first = text_field("Prénom")
    last = text_field("Nom")
    phone = text_field("Téléphone")
    country = text_field("Pays")
    language = ft.Dropdown(label="Langue", options=[ft.dropdown.Option("fr", "Français"), ft.dropdown.Option("en", "English")], value="fr")

    def refresh():
        r = state["api"].profile()
        if r and r.status_code == 200:
            d = r.json()
            info.value = f"{d['email']}\nCréé le {d['created_at'][:10]}"
            first.value = d.get("first_name", "")
            last.value = d.get("last_name", "")
            phone.value = d.get("phone", "")
            country.value = d.get("country", "")
            language.value = d.get("preferred_language", "fr")
        page.update()

    def save(e):
        payload = {"first_name": first.value, "last_name": last.value, "phone": phone.value, "country": country.value, "preferred_language": language.value}
        r = state["api"].request("PATCH", "/api/v1/accounts/me/", json=payload)
        if r and r.status_code == 200:
            state["user"] = r.json()
            snackbar(page, "Profil mis à jour.")
        else:
            snackbar(page, error_message(r), error=True)

    def logout(e):
        state["api"].logout()
        state["api"].clear()
        state["user"] = None
        navigate("login")

    refresh()

    return ft.View(route="/profile",
        appbar=ft.AppBar(title=ft.Text("Profil", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("dashboard"), icon_color="white")),
        controls=[ft.Container(content=ft.Column([card(info), first, last, phone, country, language, button("Enregistrer", save),
                                                button("Se déconnecter", logout, primary=False)]), padding=16)],
    )
