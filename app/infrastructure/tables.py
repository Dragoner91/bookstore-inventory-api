from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, Numeric, func
from sqlmodel import Field, SQLModel

from app.domain.book import Book


class BookTable(SQLModel, table=True):
    __tablename__ = "books"

    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: str
    isbn: str = Field(unique=True) #Unique
    cost_usd: Decimal = Field(sa_column=Column(Numeric(14, 2), nullable=False))
    selling_price_local: Decimal | None = Field(
        default=None, sa_column=Column(Numeric(14, 2))
    )
    stock_quantity: int
    category: str
    supplier_country: str
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        ),
    )


def to_domain(row: BookTable) -> Book:
    return Book(**row.model_dump())


def to_table(book: Book) -> BookTable:
    # exclude_none deja que la base ponga id, created_at y updated_at por su cuenta
    return BookTable(**book.model_dump(exclude_none=True))
