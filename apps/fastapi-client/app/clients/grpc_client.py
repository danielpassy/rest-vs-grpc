"""gRPC client for the GibberishService."""

import grpc.aio

from app.gen.gibberish.v1 import gibberish_pb2, gibberish_pb2_grpc
from app.schema import GibberishPayload, ProcessResult
from app import settings


async def call_grpc(payload: GibberishPayload) -> ProcessResult:
    """Call GibberishService.Process over gRPC."""
    proto_items = [
        gibberish_pb2.Item(
            id=item.id,
            label=item.label,
            value=item.value,
            tags=item.tags,
            metadata=item.metadata,
        )
        for item in payload.items
    ]

    proto_payload = gibberish_pb2.GibberishPayload(
        request_id=payload.request_id,
        timestamp=payload.timestamp,
        source=payload.source,
        items=proto_items,
        checksum=payload.checksum,
    )

    target = f"{settings.GO_SERVER_GRPC_HOST}:{settings.GO_SERVER_GRPC_PORT}"
    async with grpc.aio.insecure_channel(target) as channel:
        stub = gibberish_pb2_grpc.GibberishServiceStub(channel)
        result = await stub.Process(
            proto_payload,
            metadata=(
                ("authorization", f"Bearer {settings.GO_SERVER_AUTH_TOKEN}"),
            ),
        )

    return ProcessResult(
        request_id=result.request_id,
        processed_at=result.processed_at,
        item_count=result.item_count,
        value_sum=result.value_sum,
        dominant_tag=result.dominant_tag,
        status=result.status,
    )
