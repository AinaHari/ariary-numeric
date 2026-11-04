import flet as ft

from mobile.components.common import *


def build_notifications(page, state, navigate):
    lst = ft.Column(scroll=ft.ScrollMode.AUTO)

    def refresh():
        lst.controls.clear()
        r = state["api"].notifications()
        if r and r.status_code == 200:
            for n in as_list(r):
                lst.controls.append(
                    ft.ListTile(
                        title=ft.Text(n["title"]),
                        subtitle=ft.Text(f"{n['message']}\n{n['created_at'][:19]}"),
                        trailing=ft.Icon(ft.Icons.MARK_EMAIL_READ if n["is_read"] else ft.Icons.MAIL),
                        on_click=lambda e, pk=n["id"]: mark_read(pk),
                    )
                )
        if not lst.controls:
            lst.controls.append(ft.Text("Aucune notification."))
        page.update()

    def mark_read(pk):
        state["api"].mark_read(pk)
        refresh()

    def mark_all(e):
        state["api"].mark_all_read()
        refresh()

    refresh()

    return ft.View(route="/notifications",
        appbar=ft.AppBar(title=ft.Text("Notifications", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("dashboard"), icon_color="white")),
        controls=[ft.Container(content=ft.Column([button("Tout marquer comme lu", mark_all, primary=False), lst]), padding=16)],
    )
