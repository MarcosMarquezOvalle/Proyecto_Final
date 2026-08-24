from __future__ import annotations

import sqlite3

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

from proyecto_final.main import create_app


def _run_migration(database_path: str) -> None:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")
    command.upgrade(alembic_cfg, "head")


def test_e2e_login_and_order_lifecycle(tmp_path) -> None:
    database_path = tmp_path / "orders.db"
    _run_migration(str(database_path))

    client = TestClient(create_app(api_key="test-key", database_path=str(database_path)))

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
            "customer_id": "CUST-42",
            "items": [{"sku": "SKU-2", "quantity": 3, "unit_price": "7.50"}],
        },
    )
    assert create_response.status_code == 201
    created_order = create_response.json()
    order_id = created_order["id"]

    list_response = client.get("/orders", headers=headers)
    assert list_response.status_code == 200
    assert any(item["id"] == order_id for item in list_response.json())

    patch_response = client.patch(
        f"/orders/{order_id}/status",
        headers=headers,
        json={"status": "confirmed"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == "confirmed"

    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            "SELECT COUNT(*) FROM orders WHERE id = ? AND status = 'confirmed'",
            (order_id,),
        ).fetchone()
    assert row is not None and row[0] == 1


def test_alembic_creates_tables_for_orders_and_users(tmp_path) -> None:
    database_path = tmp_path / "orders.db"
    _run_migration(str(database_path))

    with sqlite3.connect(database_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()

    table_names = {table[0] for table in tables}
    assert {"orders", "users"}.issubset(table_names)
