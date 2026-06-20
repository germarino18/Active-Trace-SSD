# -*- coding: utf-8 -*-
"""Test all alumno endpoints after seed data update."""
import httpx
import sys

BASE = "http://localhost:8000"
TENANT_ID = "e193e975-b2c4-495c-8566-45d045866ae8"


def main():
    with httpx.Client() as client:
        resp = client.post(
            f"{BASE}/api/auth/authenticate",
            json={"email": "alumno@demo.com", "password": "Alumno123!"},
            headers={"X-Tenant-ID": TENANT_ID},
        )
        if resp.status_code != 200:
            print(f"[FAIL] Auth failed: {resp.status_code} {resp.text[:200]}")
            sys.exit(1)
        data = resp.json()
        token = data.get("token") or data.get("access_token") or ""
        if not token:
            print(f"[FAIL] No token in response: {data}")
            sys.exit(1)
        print(f"[OK] Auth OK (token: {token[:20]}...)")

        headers = {
            "Authorization": f"Bearer {token}",
            "X-Tenant-ID": TENANT_ID,
        }

        endpoints = [
            ("GET", "/api/v1/alumno/dashboard"),
            ("GET", "/api/v1/alumno/comunicaciones"),
            ("GET", "/api/v1/inbox/hilos"),
            ("GET", "/api/v1/avisos/visible"),
            ("GET", "/api/v1/alumno/materias"),
            ("GET", "/api/v1/alumno/programas"),
            ("GET", "/api/v1/alumno/fechas"),
        ]

        for method, path in endpoints:
            resp = client.request(method, f"{BASE}{path}", headers=headers)
            try:
                body = resp.json()
            except Exception:
                body = resp.text[:200]

            status = resp.status_code
            if status == 200:
                if isinstance(body, dict):
                    keys = list(body.keys())[:5]
                    summary = f"dict with keys: {keys}"
                elif isinstance(body, list):
                    summary = f"list with {len(body)} items"
                    if body:
                        summary += f" (first: {str(body[0])[:120]})"
                else:
                    summary = str(body)[:150]
                print(f"[OK] {path} -> 200 ({summary})")
            elif status == 403:
                detail = body.get("detail", {})
                if isinstance(detail, dict):
                    msg = detail.get("message", str(detail))
                else:
                    msg = str(detail)[:100]
                print(f"[DENY] {path} -> 403 ({msg})")
            else:
                print(f"[FAIL] {path} -> {status} ({str(body)[:200]})")


if __name__ == "__main__":
    main()
