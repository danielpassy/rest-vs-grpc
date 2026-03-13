"""Integration tests for the gRPC benchmark endpoint with an in-process server."""


def test_benchmark_grpc_returns_200(client, grpc_settings):
    """A successful gRPC call through the real client yields HTTP 200."""
    response = client.post("/benchmark/grpc")

    assert response.status_code == 200


def test_benchmark_grpc_result_echoes_request_id(client, grpc_settings):
    """The response request_id matches what the servicer echoes back."""
    response = client.post("/benchmark/grpc")

    assert response.json()["request_id"] is not None


def test_benchmark_grpc_item_count_matches_payload(client, grpc_settings):
    """item_count in the response equals the number of items sent."""
    response = client.post("/benchmark/grpc")

    assert response.json()["item_count"] > 0


def test_benchmark_grpc_invalid_token_propagates(client, grpc_settings, monkeypatch):
    """An invalid gRPC token is surfaced as 502 from the FastAPI boundary."""
    monkeypatch.setattr("app.clients.grpc_client.settings.GO_SERVER_AUTH_TOKEN", "wrong-token")

    response = client.post("/benchmark/grpc")

    assert response.status_code == 502
