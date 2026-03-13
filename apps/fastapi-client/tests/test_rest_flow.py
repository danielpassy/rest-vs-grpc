"""Integration tests for the REST benchmark endpoint using a mocked Go server."""

import httpx
import respx


PROCESS_URL = "http://localhost:8080/process"

VALID_PROCESS_RESULT = {
    "request_id": "abc",
    "processed_at": "2024-01-01T00:00:00Z",
    "item_count": 10,
    "value_sum": 500.0,
    "dominant_tag": "foo",
    "status": "ok",
}


def test_benchmark_rest_returns_200(client):
    """A successful Go server response yields HTTP 200 from the benchmark endpoint."""
    with respx.mock:
        route = respx.post(PROCESS_URL).mock(
            return_value=httpx.Response(200, json=VALID_PROCESS_RESULT)
        )
        response = client.post("/benchmark/rest")

    assert response.status_code == 200
    assert route.calls.last.request.headers["Authorization"] == "Bearer dev-token"


def test_benchmark_rest_result_echoes_request_id(client):
    """The response body contains the request_id returned by the Go server."""
    with respx.mock:
        respx.post(PROCESS_URL).mock(
            return_value=httpx.Response(200, json=VALID_PROCESS_RESULT)
        )
        response = client.post("/benchmark/rest")

    assert response.json()["request_id"] == VALID_PROCESS_RESULT["request_id"]


def test_benchmark_rest_go_server_error_propagates(client):
    """A 500 from the Go server is surfaced as 502 Bad Gateway."""
    with respx.mock:
        respx.post(PROCESS_URL).mock(
            return_value=httpx.Response(500, json={"error": "internal server error"})
        )
        response = client.post("/benchmark/rest")

    assert response.status_code == 502
