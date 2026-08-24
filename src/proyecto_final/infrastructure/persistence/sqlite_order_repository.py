from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from proyecto_final.application.ports import OrderRepository
from proyecto_final.domain.order import Order, OrderItem, OrderStatus


class SqliteOrderRepository(OrderRepository):
    def __init__(self, database_path: str | Path | None = None) -> None:
        self.database_path = (
            Path(database_path) if database_path is not None else self._default_path()
        )
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @staticmethod
    def _default_path() -> Path:
        return Path(__file__).resolve().parents[3] / "orders.db"

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    items_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )

    def add(self, order: Order) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO orders (id, customer_id, items_json, created_at, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(order.id),
                    order.customer_id,
                    self._serialize_items(order.items),
                    order.created_at.isoformat(),
                    order.status.value,
                ),
            )

    def get(self, order_id: UUID) -> Order | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM orders WHERE id = ?",
                (str(order_id),),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_order(row)

    def list(self) -> list[Order]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
        return [self._row_to_order(row) for row in rows]

    def update(self, order: Order) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE orders
                SET customer_id = ?, items_json = ?, created_at = ?, status = ?
                WHERE id = ?
                """,
                (
                    order.customer_id,
                    self._serialize_items(order.items),
                    order.created_at.isoformat(),
                    order.status.value,
                    str(order.id),
                ),
            )

    @staticmethod
    def _serialize_items(items: tuple[OrderItem, ...]) -> str:
        payload = [
            {
                "sku": item.sku,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
            }
            for item in items
        ]
        return json.dumps(payload)

    @staticmethod
    def _row_to_order(row: sqlite3.Row) -> Order:
        payload = json.loads(row["items_json"])
        items = tuple(
            OrderItem(
                sku=item["sku"],
                quantity=int(item["quantity"]),
                unit_price=Decimal(str(item["unit_price"])),
            )
            for item in payload
        )
        return Order(
            id=UUID(row["id"]),
            customer_id=row["customer_id"],
            items=items,
            created_at=datetime.fromisoformat(row["created_at"]),
            status=OrderStatus(row["status"]),
        )
