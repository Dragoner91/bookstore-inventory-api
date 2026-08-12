from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.schemas import BookCreate, BookUpdate
from app.application.book_service import BookService
from app.application.pricing_service import PricingService
from app.config import settings
from app.domain.book import Book
from app.domain.price import PriceCalculation
from app.infrastructure.book_repository import PostgresBookRepository
from app.infrastructure.database import get_session
from app.infrastructure.exchange_api import ExchangeRateApiProvider

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_book_service(session: SessionDep) -> BookService:
    return BookService(PostgresBookRepository(session))


def get_pricing_service(request: Request, session: SessionDep) -> PricingService:
    return PricingService(
        PostgresBookRepository(session),
        # el cliente HTTP compartido que abre el lifespan
        ExchangeRateApiProvider(request.app.state.http_client),
        settings.margin_percentage,
    )


BookServiceDep = Annotated[BookService, Depends(get_book_service)]
PricingServiceDep = Annotated[PricingService, Depends(get_pricing_service)]

router = APIRouter()


@router.post("", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(payload: BookCreate, service: BookServiceDep) -> Book:
    return await service.create(Book(**payload.model_dump()))


@router.get("", response_model=list[Book])
async def list_books(
    service: BookServiceDep,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[Book]:
    return await service.list_books(limit, offset)


# /search y /low-stock van antes que /{book_id}: si no, FastAPI toma "search"
# como si fuera un id y falla al convertirlo a entero
@router.get("/search", response_model=list[Book])
async def search_by_category(category: str, service: BookServiceDep) -> list[Book]:
    return await service.find_by_category(category)


@router.get("/low-stock", response_model=list[Book])
async def find_low_stock(
    service: BookServiceDep, threshold: int = Query(10, ge=0)
) -> list[Book]:
    return await service.find_low_stock(threshold)


@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: int, service: BookServiceDep) -> Book:
    return await service.get(book_id)


@router.put("/{book_id}", response_model=Book)
async def update_book(
    book_id: int, payload: BookUpdate, service: BookServiceDep
) -> Book:
    return await service.update(book_id, payload.model_dump(exclude_unset=True))


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, service: BookServiceDep) -> None:
    await service.delete(book_id)


@router.post("/{book_id}/calculate-price", response_model=PriceCalculation)
async def calculate_price(
    book_id: int, service: PricingServiceDep
) -> PriceCalculation:
    return await service.calculate(book_id)
