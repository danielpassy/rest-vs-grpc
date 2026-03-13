"""Shared pytest fixtures for the fastapi-client test suite."""

from concurrent import futures

import grpc
import pytest
from fastapi.testclient import TestClient
from grpc import StatusCode

from app.gen.gibberish.v1 import gibberish_pb2, gibberish_pb2_grpc
from app.main import app


class FakeGibberishServicer(gibberish_pb2_grpc.GibberishServiceServicer):
    """In-process test double for the Go gRPC server."""

    def Process(self, request, context):
        """Echo request_id back and compute item_count and value_sum from the request."""
        metadata = dict(context.invocation_metadata())
        if metadata.get("authorization") != "Bearer dev-token":
            context.abort(StatusCode.UNAUTHENTICATED, "invalid token")

        return gibberish_pb2.ProcessResult(
            request_id=request.request_id,
            processed_at="2024-01-01T00:00:00Z",
            item_count=len(request.items),
            value_sum=sum(item.value for item in request.items),
            dominant_tag="foo",
            status="ok",
        )


@pytest.fixture(scope="session")
def grpc_server():
    """Start an in-process gRPC server for the session and return its address."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    gibberish_pb2_grpc.add_GibberishServiceServicer_to_server(FakeGibberishServicer(), server)
    port = server.add_insecure_port("localhost:0")
    server.start()
    yield f"localhost:{port}"
    server.stop(grace=0)


@pytest.fixture
def grpc_settings(grpc_server, monkeypatch):
    """Point grpc_client settings at the in-process fake server."""
    host, port = grpc_server.split(":")
    monkeypatch.setattr("app.clients.grpc_client.settings.GO_SERVER_GRPC_HOST", host)
    monkeypatch.setattr("app.clients.grpc_client.settings.GO_SERVER_GRPC_PORT", port)


@pytest.fixture
def client():
    """Return a synchronous TestClient wrapping the FastAPI app."""
    return TestClient(app)
