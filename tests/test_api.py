from __future__ import annotations

from fastapi.testclient import TestClient

from proyecto_final.main import create_app


def test_orders_api_flow(tmp_path) -> None:
    client = TestClient(create_app(api_key="test-key", database_path=str(tmp_path / "orders.db")))

    login_response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/orders",
        headers=headers,
        json={
            "customer_id": "CUST-1",
            "items": [{"sku": "SKU-1", "quantity": 2, "unit_price": "19.99"}],
        },
    )
    assert create_response.status_code == 201
    payload = create_response.json()
    order_id = payload["id"]
    assert payload["status"] == "pending"
    assert payload["total_amount"] == "39.98"

    get_response = client.get(f"/orders/{order_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == order_id

    update_response = client.patch(
        f"/orders/{order_id}/status",
        headers=headers,
        json={"status": "confirmed"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "confirmed"


def test_api_requires_authentication(tmp_path) -> None:
    client = TestClient(create_app(api_key="test-key", database_path=str(tmp_path / "orders.db")))

    response = client.get("/orders")
    assert response.status_code == 401
