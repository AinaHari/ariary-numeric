import os
import qrcode

import flet as ft

from mobile.components.common import *


def build_qr(page, state, navigate):
    user = state.get("user") or {}
    email = user.get("email", "")
    payload = f"ariary://pay?to={email}"
    qr_path = os.path.join(tempfile.gettempdir(), "ariary_qr.png")
    os.makedirs(tempfile.gettempdir(), exist_ok=True)
    try:
        img = qrcode.make(payload)
        img.save(qr_path)
    except Exception:
        qr_path = None

    scan_input = text_field("Code scanné / payload")

    def confirm_scan(e):
        # expected payload ariary://pay?to=email
        val = scan_input.value.strip()
        if not val:
            snackbar(page, "Payload vide.", error=True)
            return
        to_email = val
        if "to=" in val:
            to_email = val.split("to=")[-1]
        state["scan_recipient"] = to_email
        snackbar(page, f"Destinataire : {to_email}")
        navigate("qrconfirm")

    controls = [
        ft.Text("Recevoir", weight=ft.FontWeight.BOLD),
        ft.Text(f"Votre code de réception : {email}"),
    ]
    if qr_path and os.path.exists(qr_path):
        controls.append(ft.Image(src=qr_path, width=220, height=220))
    controls += [
        ft.Container(height=10),
        ft.Text("Scanner (saisie manuelle si caméra indisponible)", weight=ft.FontWeight.BOLD),
        scan_input,
        button("Vérifier", confirm_scan),
    ]

    return ft.View(route="/qr",
        appbar=ft.AppBar(title=ft.Text("QR Code", color="white"), bgcolor=PRIMARY,
                         leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("dashboard"), icon_color="white")),
        controls=[ft.Container(content=ft.Column(controls, scroll=ft.ScrollMode.AUTO), padding=16)],
    )
