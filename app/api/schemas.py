from decimal import Decimal

from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    cost_usd: Decimal
    stock_quantity: int
    category: str
    supplier_country: str


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    isbn: str | None = None
    cost_usd: Decimal | None = None
    stock_quantity: int | None = None
    category: str | None = None
    supplier_country: str | None = None
