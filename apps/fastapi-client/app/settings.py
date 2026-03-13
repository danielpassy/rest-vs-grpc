import os

GO_SERVER_REST_URL = os.getenv("GO_SERVER_REST_URL", "http://localhost:8080")
GO_SERVER_GRPC_HOST = os.getenv("GO_SERVER_GRPC_HOST", "localhost")
GO_SERVER_GRPC_PORT = int(os.getenv("GO_SERVER_GRPC_PORT", "50051"))
GO_SERVER_AUTH_TOKEN = os.getenv("GO_SERVER_AUTH_TOKEN", "dev-token")
ITEMS_PER_PAYLOAD = 10
