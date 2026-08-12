from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.infrastructure.database import create_tables, engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await create_tables()
    # un unico cliente para toda la app: crear uno por request tira el pool de
    # conexiones y suma el handshake TLS a cada llamada
    app.state.http_client = httpx.AsyncClient()
    yield
    await app.state.http_client.aclose()
    await engine.dispose()


app = FastAPI(
    title="Bookstore Inventory API",
    description="Gestion de inventario de librerias con calculo de precio de venta sugerido.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {"status": "ok"}
