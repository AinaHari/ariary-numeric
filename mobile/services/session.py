"""Persistance légère de la session.

Seul le jeton d'API est conservé (jamais le mot de passe). Flet 1.x
expose ``SharedPreferences`` via un service asynchrone ; on garde donc
une valeur en mémoire (utilisée immédiatement par l'UI) et une écriture
différée vers le stockage natif.
"""

import asyncio

import flet as ft

KEY = "ariary_token"


class TokenStore:
    def __init__(self):
        self.value = None
        self._prefs = None

    def attach(self, page):
        """À appeler une fois dans ``main(page)`` après création de la page."""
        try:
            prefs = ft.SharedPreferences()
            page.services.append(prefs)
            self._prefs = prefs
            asyncio.create_task(self._hydrate())
        except Exception:
            self._prefs = None

    async def _hydrate(self):
        try:
            saved = await self._prefs.get(KEY)
            if saved and not self.value:
                self.value = saved
        except Exception:
            pass

    def set(self, token):
        self.value = token
        self._write(token)

    def remove(self):
        self.value = None
        self._write(None)

    def _write(self, token):
        if not self._prefs:
            return
        try:
            asyncio.create_task(self._persist(token))
        except Exception:
            pass

    async def _persist(self, token):
        try:
            if token:
                await self._prefs.set(KEY, token)
            else:
                await self._prefs.remove(KEY)
        except Exception:
            pass
