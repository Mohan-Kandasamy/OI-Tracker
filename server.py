import json
import os
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from dotenv import load_dotenv
from py5paisa import FivePaisaClient

load_dotenv(Path(__file__).resolve().parent / '.env')

ROOT = Path(__file__).resolve().parent
state = {"token": None, "config": None}
client = None


def normalize_connection_config(payload):
    if not isinstance(payload, dict):
        return None
    cleaned = {
        "app_source": str(payload.get("app_source") or payload.get("APP_SOURCE") or "").strip(),
        "app_name": str(payload.get("app_name") or payload.get("APP_NAME") or "").strip(),
        "user_id": str(payload.get("user_id") or payload.get("USER_ID") or "").strip(),
        "password": str(payload.get("password") or payload.get("PASSWORD") or "").strip(),
        "user_key": str(payload.get("user_key") or payload.get("USER_KEY") or "").strip(),
        "encryption_key": str(payload.get("encryption_key") or payload.get("ENCRYPTION_KEY") or "").strip(),
    }
    market_data_url = payload.get("market_data_url") or payload.get("MARKET_DATA_URL") or ""
    if market_data_url:
        cleaned["market_data_url"] = str(market_data_url).strip()
    if not all(cleaned.values()):
        return None
    return cleaned


def get_client(config=None):
    global client
    if client is not None and config is None:
        return client
    active_config = config or state.get("config")
    if active_config is None:
        app_source = os.getenv("FIVE_PAISA_APP_SOURCE")
        app_name = os.getenv("FIVE_PAISA_APP_NAME")
        user_id = os.getenv("FIVE_PAISA_USER_ID")
        password = os.getenv("FIVE_PAISA_PASSWORD")
        user_key = os.getenv("FIVE_PAISA_USER_KEY")
        encryption_key = os.getenv("FIVE_PAISA_ENCRYPTION_KEY")
        if not all([app_source, app_name, user_id, password, user_key, encryption_key]):
            return None
        active_config = {
            "app_source": app_source,
            "app_name": app_name,
            "user_id": user_id,
            "password": password,
            "user_key": user_key,
            "encryption_key": encryption_key,
        }
    cred = {
        "APP_SOURCE": active_config.get("app_source") or active_config.get("APP_SOURCE") or "",
        "APP_NAME": active_config.get("app_name") or active_config.get("APP_NAME") or "",
        "USER_ID": active_config.get("user_id") or active_config.get("USER_ID") or "",
        "PASSWORD": active_config.get("password") or active_config.get("PASSWORD") or "",
        "USER_KEY": active_config.get("user_key") or active_config.get("USER_KEY") or "",
        "ENCRYPTION_KEY": active_config.get("encryption_key") or active_config.get("ENCRYPTION_KEY") or "",
    }
    if not all(cred.values()):
        return None
    client = FivePaisaClient(cred=cred)
    return client


def json_response(handler, status, payload):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/5paisa/auth":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            try:
                payload = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                payload = {}
            token = payload.get("token") or payload.get("access_token")
            if token:
                state["token"] = token
                return json_response(self, 200, {"status": "ok", "tokenStored": True})
            return json_response(self, 400, {"status": "error", "message": "Missing token"})

        if self.path == "/api/5paisa/config":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            try:
                payload = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                payload = {}
            config = normalize_connection_config(payload)
            if not config:
                return json_response(self, 400, {"status": "error", "message": "Missing connection fields"})
            state["config"] = config
            token = payload.get("access_token") or payload.get("token")
            if token:
                state["token"] = token
            global client
            client = None
            return json_response(self, 200, {"status": "ok", "connected": True, "message": "Connection configuration saved for this session"})
        return json_response(self, 404, {"status": "error", "message": "Not found"})

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/5paisa/health":
            return json_response(self, 200, {"status": "ok", "connected": bool(state.get("config")), "tokenStored": bool(state.get("token"))})

        if parsed.path == "/api/5paisa/market-data":
            params = urllib.parse.parse_qs(parsed.query)
            underlying = params.get("underlying", ["nifty"])[0]
            expiry = params.get("expiry", ["2026-07-30"])[0]
            interval = params.get("interval", ["5"])[0]
            auth_header = self.headers.get("Authorization", "")
            token = state.get("token") or auth_header.replace("Bearer ", "", 1).strip()

            client_obj = get_client()
            if client_obj is not None and token:
                try:
                    client_obj.set_access_token(token)
                    payload = client_obj.get_option_chain(underlying=underlying, expiry=expiry)
                    if isinstance(payload, dict):
                        return json_response(self, 200, payload)
                    if isinstance(payload, list):
                        return json_response(self, 200, {"rows": payload})
                except Exception as exc:  # pragma: no cover - runtime fallback
                    pass

            target_url = state.get("config", {}).get("market_data_url") if state.get("config") else None
            if target_url:
                try:
                    req = urllib.request.Request(target_url, headers={"Authorization": f"Bearer {token}" if token else ""})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        payload = json.load(resp)
                    return json_response(self, 200, payload)
                except Exception as exc:  # pragma: no cover - runtime fallback
                    return json_response(self, 502, {"status": "error", "message": str(exc)})

            rows = []
            for i in range(9):
                strike = 23850 + i * 50
                if underlying.lower() == "sensex":
                    strike = 78900 + i * 100
                if underlying.lower() == "sensex":
                    diff = (i % 3) - 1
                else:
                    diff = (i % 4) - 1
                change_put = 4 + i * 2 + (1 if diff > 0 else 0)
                change_call = 3 + i + (1 if diff < 0 else 0)
                rows.append({
                    "strike": strike,
                    "ltp": 2200 + i * 10,
                    "changeInPutOi": change_put,
                    "changeInCallOi": change_call,
                    "time": f"{9 + i}:{15 + (i % 5) * 5}",
                })
            return json_response(self, 200, {"rows": rows})

        if parsed.path in {"/", "/index.html", "/orb-dashboard.html"}:
            file_name = "index.html" if parsed.path in {"/", "/index.html"} else "orb-dashboard.html"
            file_path = ROOT / file_name
            if file_path.exists():
                body = file_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

        if parsed.path == "/data.json":
            file_path = ROOT / "data.json"
            if file_path.exists():
                body = file_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

        return json_response(self, 404, {"status": "error", "message": "Not found"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    httpd = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving on http://0.0.0.0:{port}")
    httpd.serve_forever()
