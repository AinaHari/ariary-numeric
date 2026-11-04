import httpx

from mobile.config import API_BASE_URL


class ApiClient:
    def __init__(self):
        self.base = API_BASE_URL.rstrip("/")
        self.token = None

    def set_token(self, token):
        self.token = token

    def clear(self):
        self.token = None

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Token {self.token}"
        return h

    def request(self, method, path, json=None, files=None, data=None, timeout=30):
        url = self.base + path
        try:
            with httpx.Client(timeout=timeout) as c:
                if files:
                    h = {}
                    if self.token:
                        h["Authorization"] = f"Token {self.token}"
                    r = c.request(method, url, headers=h, files=files, data=data, timeout=timeout)
                else:
                    r = c.request(method, url, headers=self._headers(), json=json, data=data, timeout=timeout)
            return r
        except Exception as e:
            return None

    def register(self, email, password, password_confirm, first_name="", last_name="", phone="", country="Madagascar"):
        return self.request("POST", "/api/v1/accounts/register/", json={
            "email": email, "password": password, "password_confirm": password_confirm,
            "first_name": first_name, "last_name": last_name, "phone": phone, "country": country,
        })

    def login(self, email, password):
        return self.request("POST", "/api/v1/accounts/login/", json={"email": email, "password": password})

    def logout(self):
        return self.request("POST", "/api/v1/accounts/logout/")

    def profile(self):
        return self.request("GET", "/api/v1/accounts/me/")

    def wallet(self):
        return self.request("GET", "/api/v1/wallet/wallet/")

    def transactions(self):
        return self.request("GET", "/api/v1/wallet/transactions/")

    def transaction_detail(self, ref):
        return self.request("GET", f"/api/v1/wallet/transactions/{ref}/")

    def transfer(self, recipient_email, amount, description="", idempotency_key=None):
        payload = {"recipient_email": recipient_email, "amount": str(amount), "description": description}
        if idempotency_key:
            payload["idempotency_key"] = idempotency_key
        return self.request("POST", "/api/v1/wallet/transfer/", json=payload)

    def topup_demo(self, amount):
        return self.request("POST", "/api/v1/wallet/topup-demo/", json={"amount": str(amount)})

    def shipments(self):
        return self.request("GET", "/api/v1/logistics/shipments/")

    def create_shipment(self, payload):
        return self.request("POST", "/api/v1/logistics/shipments/", json=payload)

    def shipment_detail(self, ref):
        return self.request("GET", f"/api/v1/logistics/shipments/{ref}/")

    def add_shipment_event(self, ref, status, location="", description=""):
        return self.request("POST", f"/api/v1/logistics/shipments/{ref}/events/", json={
            "status": status, "location": location, "description": description,
        })

    def customs_cases(self):
        return self.request("GET", "/api/v1/customs/cases/")

    def create_customs_case(self, payload):
        return self.request("POST", "/api/v1/customs/cases/", json=payload)

    def customs_detail(self, ref):
        return self.request("GET", f"/api/v1/customs/cases/{ref}/")

    def customs_event(self, ref, status, description=""):
        return self.request("POST", f"/api/v1/customs/cases/{ref}/events/", json={"status": status, "description": description})

    def toggle_requirement(self, ref, req_id):
        return self.request("POST", f"/api/v1/customs/cases/{ref}/requirements/{req_id}/toggle/")

    def blockchain_info(self):
        return self.request("GET", "/api/v1/blockchain/info/")

    def blockchain_records(self):
        return self.request("GET", "/api/v1/blockchain/records/")

    def create_blockchain_record(self, record_type, payload):
        return self.request("POST", "/api/v1/blockchain/records/", json={"record_type": record_type, "payload": payload})

    def blockchain_verify(self, payload=None, data_hash=None):
        body = {}
        if payload is not None:
            body["payload"] = payload
        if data_hash:
            body["data_hash"] = data_hash
        return self.request("POST", "/api/v1/blockchain/verify/", json=body)

    def rates(self):
        return self.request("GET", "/api/v1/payments/rates/")

    def intl_estimate(self, payload):
        return self.request("POST", "/api/v1/payments/international/estimate/", json=payload)

    def intl_list(self):
        return self.request("GET", "/api/v1/payments/international/")

    def connectors(self):
        return self.request("GET", "/api/v1/payments/connectors/")

    def mobile_money_info(self):
        return self.request("GET", "/api/v1/payments/mobile-money/info/")

    def notifications(self):
        return self.request("GET", "/api/v1/notifications/")

    def mark_read(self, pk):
        return self.request("POST", f"/api/v1/notifications/{pk}/read/")

    def mark_all_read(self):
        return self.request("POST", "/api/v1/notifications/read-all/")
