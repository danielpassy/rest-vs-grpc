"""Pydantic v2 models matching the gRPC proto definitions."""

from pydantic import BaseModel


class Item(BaseModel):
    """A single data item with metadata."""

    id: str
    label: str
    value: float
    tags: list[str]
    metadata: dict[str, str]


class GibberishPayload(BaseModel):
    """A payload containing a collection of items for processing."""

    request_id: str
    timestamp: str
    source: str
    items: list[Item]
    checksum: int


class ProcessResult(BaseModel):
    """The result of processing a GibberishPayload."""

    request_id: str
    processed_at: str
    item_count: int
    value_sum: float
    dominant_tag: str
    status: str
