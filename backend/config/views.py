"""Vues utilitaires du projet (page d'accueil API)."""
from django.conf import settings
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


def presentation(request):
    from django.http import FileResponse
    import os
    path = os.path.join(settings.BASE_DIR, 'static', 'presentation', 'index.html')
    return FileResponse(open(path, 'rb'), content_type='text/html')

def serve_static_file(request, filename):
    from django.http import FileResponse
    import os
    content_types = {
        'manifest.json': 'application/manifest+json',
        'sw.js': 'application/javascript',
        'robots.txt': 'text/plain',
        'sitemap.xml': 'application/xml',
    }
    path = os.path.join(settings.BASE_DIR, '..', 'public', filename)
    if not os.path.exists(path):
        path = os.path.join(settings.BASE_DIR, 'static', filename)
    if not os.path.exists(path):
        from django.http import Http404
        raise Http404
    return FileResponse(open(path, 'rb'), content_type=content_types.get(filename, 'application/octet-stream'))


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
    from django.db import connection
    try:
        with connection.cursor() as c:
            c.execute("SELECT 1")
        db_ok = True
    except Exception:
        db_ok = False
    status_code = 200 if db_ok else 503
    return JsonResponse({"status": "ok" if db_ok else "degraded", "database": db_ok}, status=status_code)
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
