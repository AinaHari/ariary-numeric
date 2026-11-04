"""Vues utilitaires du projet (page d'accueil API)."""
from django.http import JsonResponse

ENDPOINTS = {
    "admin": "/admin/",
    "accounts": {
        "register": "POST /api/v1/accounts/register/",
        "login": "POST /api/v1/accounts/login/",
        "logout": "POST /api/v1/accounts/logout/",
        "me": "GET-PATCH /api/v1/accounts/me/",
    },
    "wallet": {
        "wallet": "GET /api/v1/wallet/wallet/",
        "transactions": "GET /api/v1/wallet/transactions/",
        "transaction_detail": "GET /api/v1/wallet/transactions/{reference}/",
        "transfer": "POST /api/v1/wallet/transfer/",
        "topup-demo": "POST /api/v1/wallet/topup-demo/",
    },
    "logistics": {"shipments": "/api/v1/logistics/shipments/"},
    "customs": {"cases": "/api/v1/customs/cases/"},
    "blockchain": {"info": "GET /api/v1/blockchain/info/", "records": "/api/v1/blockchain/records/", "verify": "POST /api/v1/blockchain/verify/"},
    "payments": {"rates": "GET /api/v1/payments/rates/", "international/estimate": "POST /api/v1/payments/international/estimate/", "mobile-money/info": "GET /api/v1/payments/mobile-money/info/"},
    "notifications": {"list": "GET /api/v1/notifications/", "read": "POST /api/v1/notifications/{id}/read/", "read-all": "POST /api/v1/notifications/read-all/"},
}


def healthz(request):
    from django.db import connection
    try:
        with connection.cursor() as c:
            c.execute("SELECT 1")
        db_ok = True
    except Exception:
        db_ok = False
    status_code = 200 if db_ok else 503
    return JsonResponse({"status": "ok" if db_ok else "degraded", "database": db_ok}, status=status_code)


def api_index(request):
    return JsonResponse({
        "name": "ARIARY NUMERIC",
        "description": "Portefeuille numérique de démonstration (aucun argent réel).",
        "status": "ok",
        "endpoints": ENDPOINTS,
    })
