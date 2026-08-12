import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.domain.errors import BookNotFound, DuplicateISBN, InvalidBookData

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BookNotFound)
    async def handle_book_not_found(
        request: Request, error: BookNotFound
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(error)})

    @app.exception_handler(DuplicateISBN)
    async def handle_duplicate_isbn(
        request: Request, error: DuplicateISBN
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(error)})

    @app.exception_handler(InvalidBookData)
    async def handle_invalid_book_data(
        request: Request, error: InvalidBookData
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(error)})

    @app.exception_handler(SQLAlchemyError)
    async def handle_database_error(
        request: Request, error: SQLAlchemyError
    ) -> JSONResponse:
        logger.exception("Fallo la base de datos")
        return JSONResponse(
            status_code=503,
            content={"detail": "Base de datos no disponible, intente mas tarde"},
        )
