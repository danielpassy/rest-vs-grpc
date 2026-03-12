"""Benchmark routes."""

from fastapi import APIRouter

from app.generator import generate_payload
from app.clients.rest_client import call_rest
from app.clients.grpc_client import call_grpc

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/benchmark/rest")
async def benchmark_rest():
    payload = generate_payload()
    return await call_rest(payload)


@router.post("/benchmark/grpc")
async def benchmark_grpc():
    payload = generate_payload()
    return await call_grpc(payload)
