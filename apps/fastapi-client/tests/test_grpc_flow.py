"""Integration tests for the gRPC benchmark endpoint using a mocked stub."""

from unittest.mock import MagicMock, patch


def _make_grpc_result(request_id: str = "abc") -> MagicMock:
    """Return a mock proto ProcessResult with the given request_id."""
    result = MagicMock()
    result.request_id = request_id
    result.processed_at = "2024-01-01T00:00:00Z"
    result.item_count = 10
    result.value_sum = 500.0
    result.dominant_tag = "foo"
    result.status = "ok"
    return result


def test_benchmark_grpc_returns_200(client):
    """A successful gRPC call yields HTTP 200 from the benchmark endpoint."""
    mock_result = _make_grpc_result()

    with (
        patch("app.clients.grpc_client.grpc.insecure_channel") as mock_channel_fn,
        patch("app.clients.grpc_client.gibberish_pb2_grpc.GibberishServiceStub") as mock_stub_cls,
    ):
        mock_channel = MagicMock()
        mock_channel.__enter__ = MagicMock(return_value=mock_channel)
        mock_channel.__exit__ = MagicMock(return_value=False)
        mock_channel_fn.return_value = mock_channel

        mock_stub = MagicMock()
        mock_stub.Process.return_value = mock_result
        mock_stub_cls.return_value = mock_stub

        response = client.post("/benchmark/grpc")

    assert response.status_code == 200


def test_benchmark_grpc_result_echoes_request_id(client):
    """The response body contains the request_id from the gRPC result."""
    mock_result = _make_grpc_result(request_id="test-id-42")

    with (
        patch("app.clients.grpc_client.grpc.insecure_channel") as mock_channel_fn,
        patch("app.clients.grpc_client.gibberish_pb2_grpc.GibberishServiceStub") as mock_stub_cls,
    ):
        mock_channel = MagicMock()
        mock_channel.__enter__ = MagicMock(return_value=mock_channel)
        mock_channel.__exit__ = MagicMock(return_value=False)
        mock_channel_fn.return_value = mock_channel

        mock_stub = MagicMock()
        mock_stub.Process.return_value = mock_result
        mock_stub_cls.return_value = mock_stub

        response = client.post("/benchmark/grpc")

    assert response.json()["request_id"] == "test-id-42"


def test_benchmark_grpc_stub_called_once(client):
    """The gRPC stub Process method is invoked exactly once per benchmark request."""
    mock_result = _make_grpc_result()

    with (
        patch("app.clients.grpc_client.grpc.insecure_channel") as mock_channel_fn,
        patch("app.clients.grpc_client.gibberish_pb2_grpc.GibberishServiceStub") as mock_stub_cls,
    ):
        mock_channel = MagicMock()
        mock_channel.__enter__ = MagicMock(return_value=mock_channel)
        mock_channel.__exit__ = MagicMock(return_value=False)
        mock_channel_fn.return_value = mock_channel

        mock_stub = MagicMock()
        mock_stub.Process.return_value = mock_result
        mock_stub_cls.return_value = mock_stub

        client.post("/benchmark/grpc")

        mock_stub.Process.assert_called_once()
