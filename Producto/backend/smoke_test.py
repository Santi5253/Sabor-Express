"""Smoke test end-to-end de la API SaborExpress (SQLite, usa FastAPI TestClient).

Cubre el flujo crítico de negocio:
  login -> consultar mesas/productos -> crear pedido -> consultar pedido
  -> cobrar (efectivo) -> generar reporte -> exportar Excel.
Ejecutar:  python smoke_test.py
"""
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
BASE = "/api/v1"
ok = 0


def check(cond, msg):
    global ok
    if cond:
        ok += 1
        print(f"  [OK] {msg}")
    else:
        print(f"  [FAIL] {msg}")
        raise AssertionError(msg)


def login(email, password):
    r = client.post(f"{BASE}/auth/login", json={"email": email, "password": password})
    check(r.status_code == 200, f"login {email} -> 200")
    return r.json()["access_token"], r.json()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def main():
    print("== SaborExpress API smoke test ==")

    # 1) Autenticación
    print("- Authentication")
    bad = client.post(f"{BASE}/auth/login", json={"email": "admin@saborexpress.com", "password": "wrong"})
    check(bad.status_code == 401, "wrong credentials -> 401")

    m_token, m_data = login("mesero@saborexpress.com", "Mesero@123")
    c_token, _ = login("cajero@saborexpress.com", "Cajero@123")
    a_token, _ = login("admin@saborexpress.com", "Admin@123")
    check(m_data["role"] == "Mesero", "role returned correctly")

    # 2) Catálogos
    print("- Catalogs")
    tables = client.get(f"{BASE}/tables/", headers=auth(m_token)).json()
    check(len(tables) > 0, "tables listed")
    products = client.get(f"{BASE}/admin/products/", headers=auth(m_token)).json()
    check(len(products) > 0, "products listed")

    # 3) Crear pedido (mesero)
    print("- Create order")
    p1, p2 = products[0], products[1]
    payload = {
        "table_id": tables[0]["id"],
        "guests": 2,
        "items": [
            {"product_id": p1["id"], "quantity": 2, "notes": "sin sal"},
            {"product_id": p2["id"], "quantity": 1, "notes": None},
        ],
    }
    r = client.post(f"{BASE}/orders/", json=payload, headers=auth(m_token))
    check(r.status_code == 201, "order created -> 201")
    order = r.json()
    subtotal = p1["price"] * 2 + p2["price"] * 1
    check(abs(order["total"] - subtotal) < 0.01, f"order subtotal = {subtotal}")
    check(abs(order["igv"] - round(subtotal * 0.18, 2)) < 0.01, "IGV 18% computed")
    check(order["status"] == "Open", "order status Open")
    check(len(order["items"]) == 2, "2 order items")

    # 4) Consultar pedido abierto
    print("- Query open orders")
    r = client.get(f"{BASE}/orders/open", headers=auth(c_token))
    check(r.status_code == 200 and any(o["id"] == order["id"] for o in r.json()), "open order listed")

    # 5) Pago en efectivo (cajero) — monto a pagar incluye IGV
    print("- Cash payment (amount includes IGV)")
    amount_to_pay = round(order["total"] + order["igv"], 2)
    short = client.post(f"{BASE}/payments/", json={"order_id": order["id"], "method": "Cash", "amount_given": amount_to_pay - 1}, headers=auth(c_token))
    check(short.status_code == 400, "insufficient cash -> 400")

    r = client.post(f"{BASE}/payments/", json={"order_id": order["id"], "method": "Cash", "amount_given": amount_to_pay + 5}, headers=auth(c_token))
    check(r.status_code == 201, "cash payment -> 201")
    payment = r.json()
    check(abs(payment["total_amount"] - amount_to_pay) < 0.01, f"charged total = {amount_to_pay} (with IGV)")
    check(abs(payment["change"] - 5) < 0.01, "change = 5.00")

    # 6) Pedido cerrado y mesa liberada
    print("- Order closed / table freed")
    closed = client.get(f"{BASE}/orders/{order['id']}", headers=auth(a_token)).json()
    check(closed["status"] == "Closed", "order now Closed")
    table_after = next(t for t in client.get(f"{BASE}/tables/", headers=auth(a_token)).json() if t["id"] == tables[0]["id"])
    check(table_after["status"] == "Free", "table freed after payment")

    # 7) Reportes (admin)
    print("- Reports")
    report_payload = {"branch_id": table_after["branch_id"], "date_from": "2020-01-01", "date_to": "2100-01-01"}
    r = client.post(f"{BASE}/reports/generate", json=report_payload, headers=auth(a_token))
    check(r.status_code == 200, "report generated -> 200")
    report = r.json()
    check(report["total_orders"] >= 1, "report counts the order")
    check(abs(report["total_sales"] - amount_to_pay) < 0.01, "report total sales includes IGV")

    r = client.get(f"{BASE}/reports/export", params=report_payload, headers=auth(a_token))
    check(r.status_code == 200 and len(r.content) > 0, "excel export returned bytes")
    check("spreadsheet" in r.headers.get("content-type", ""), "export content-type is xlsx")

    # 8) RBAC: mesero no accede a reportes
    print("- RBAC")
    r = client.post(f"{BASE}/reports/generate", json=report_payload, headers=auth(m_token))
    check(r.status_code == 403, "mesero forbidden on reports -> 403")

    print(f"\nAll checks passed: {ok}")
    print("Smoke test SUCCESS")


if __name__ == "__main__":
    main()
