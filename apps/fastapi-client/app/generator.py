"""Generates random GibberishPayload instances for benchmarking."""

import random
import string
import uuid
from datetime import datetime, UTC

from app.schema import GibberishPayload, Item

_WORDLIST = [
    "alpha", "bravo", "charlie", "delta", "echo",
    "foxtrot", "golf", "hotel", "india", "juliet",
    "kilo", "lima", "mike", "november", "oscar",
    "papa", "quebec", "romeo", "sierra", "tango",
]

_COLORS = ["red", "green", "blue", "yellow", "purple"]
_SIZES = ["small", "medium", "large", "xlarge"]
_PRIORITIES = ["low", "medium", "high", "critical"]


def generate_payload() -> GibberishPayload:
    """Generate a randomised GibberishPayload with 1000 large items (~10MB)."""
    items = []
    for _ in range(1000):
        item_id = str(uuid.uuid4())
        label = "".join(random.choices(string.ascii_letters + string.digits, k=2000))
        value = round(random.uniform(0.0, 1000.0), 2)
        tags = random.sample(_WORDLIST, 3)
        metadata = {
            "color": random.choice(_COLORS),
            "size": random.choice(_SIZES),
            "priority": random.choice(_PRIORITIES),
            "description": "".join(random.choices(string.ascii_letters + string.digits, k=2000)),
        }
        items.append(Item(id=item_id, label=label, value=value, tags=tags, metadata=metadata))

    checksum = sum(ord(item.id[0]) for item in items)
    timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    return GibberishPayload(
        request_id=str(uuid.uuid4()),
        timestamp=timestamp,
        source="fastapi-client",
        items=items,
        checksum=checksum,
    )
