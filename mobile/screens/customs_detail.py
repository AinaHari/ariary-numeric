import flet as ft

from mobile.components.common import *


def build_customs_detail(page, state, navigate):
    ref = state.get("selected_customs")
    info = ft.Text("Chargement...")
    reqs = ft.Column()
    events = ft.Column()
    new_status = ft.Dropdown(label="Statut", options=[
        ft.dropdown.Option("cree", "Dossier créé"),
        ft.dropdown.Option("documents_a_fournir", "Documents à fournir"),
        ft.dropdown.Option("verification", "Documents en vérification"),
        ft.dropdown.Option("formalites", "En attente de formalités"),
        ft.dropdown.Option("formalites_terminees", "Formalités terminées"),
        ft.dropdown.Option("clos", "Dossier clôturé"),
    ])
    desc = text_field("Description")

    def refresh():
        r = state["api"].customs_detail(ref)
        if r and r.status_code == 200:
            d = r.json()
            info.value = f"{d['reference']}\n{d['description']}\n{d['origin_country']} → {d['destination_country']}\nStatut: {d['status']}"
            reqs.controls.clear()
            for rq in d.get("requirements", []):
                reqs.controls.append(ft.Checkbox(label=rq["name"], value=rq["provided"],
                    on_change=lambda e, rid=rq["id"]: toggle_req(rid)))
            events.controls.clear()
            for ev in d.get("events", []):
                events.controls.append(ft.Text(f"{ev['created_at'][:19]} — {ev['status']} {ev.get('description','')}"))
        else:
            info.value = "Introuvable"
        page.update()

    def toggle_req(rid):
        state["api"].toggle_requirement(ref, rid)
        refresh()

    def add_event(e):
        if not new_status.value:
            snackbar(page, "Statut requis.", error=True)
            return
        r = state["api"].customs_event(ref, new_status.value, desc.value)
        if r and r.status_code in (200, 201):
            snackbar(page, "Mis à jour.")
            refresh()
        else:
            snackbar(page, "Erreur.", error=True)

    refresh()

    return ft.View(route="/customsdetail",
        appbar=ft.AppBar(title=ft.Text("Dossier douane", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("customs"), icon_color="white")),
        controls=[ft.Container(content=ft.Column([card(info), ft.Text("Documents requis", weight=ft.FontWeight.BOLD), reqs,
                                                 ft.Text("Historique", weight=ft.FontWeight.BOLD), events,
                                                 card(ft.Column([new_status, desc, button("Mettre à jour", add_event)]))],
                                                scroll=ft.ScrollMode.AUTO), padding=16)],
    )
