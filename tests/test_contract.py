from __future__ import annotations

from fastapi.testclient import TestClient

from proyecto_final.main import create_app


def test_openapi_contract_exposes_expected_order_endpoints(tmp_path) -> None:
    client = TestClient(create_app(api_key="test-key", database_path=str(tmp_path / "orders.db")))

    schema = client.get("/openapi.json").json()

    assert schema["info"]["title"] == "Orders Service"
    assert schema["info"]["version"] == "1.0.0"

    paths = schema["paths"]
    assert "/auth/login" in paths
    assert "/orders" in paths
    assert "/orders/{order_id}" in paths
    assert "/orders/{order_id}/status" in paths

    login_schema = (
        paths["/auth/login"]["post"]["requestBody"]["content"]["application/json"]["schema"]
    )
    assert login_schema == {"$ref": "#/components/schemas/LoginRequest"}

    create_order_schema = (
        paths["/orders"]["post"]["requestBody"]["content"]["application/json"]["schema"]
    )
    assert create_order_schema == {"$ref": "#/components/schemas/CreateOrderRequest"}

    create_request = schema["components"]["schemas"]["CreateOrderRequest"]
    assert create_request["required"] == ["customer_id", "items"]
    assert (
        create_request["properties"]["items"]["items"]["$ref"]
        == "#/components/schemas/OrderItemCreateRequest"
    )

    order_response = schema["components"]["schemas"]["OrderResponse"]
    assert order_response["required"] == [
        "id",
        "customer_id",
        "items",
        "created_at",
        "status",
        "total_amount",
    ]
    assert order_response["properties"]["status"] == {"$ref": "#/components/schemas/OrderStatus"}

    assert "HTTPBearer" in schema["components"]["securitySchemes"]
    assert schema["components"]["securitySchemes"]["HTTPBearer"]["type"] == "http"
    assert schema["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"
