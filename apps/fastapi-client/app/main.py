"""Application factory: initialises Sentry, creates the FastAPI app, and registers routes."""

import os

import grpc
import httpx
import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.router import router

sentry_dsn = os.getenv("SENTRY_DSN", "")
if sentry_dsn:
    sentry_sdk.init(dsn=sentry_dsn)

app = FastAPI()
app.include_router(router)


@app.exception_handler(httpx.HTTPStatusError)
async def httpx_error_handler(request, exc):
    return JSONResponse(status_code=502, content={"error": str(exc)})


@app.exception_handler(grpc.RpcError)
async def grpc_error_handler(request, exc):
    return JSONResponse(status_code=502, content={"error": str(exc)})
