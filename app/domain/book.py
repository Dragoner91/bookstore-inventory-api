import re
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, field_validator

from app.domain.errors import InvalidBookData

_ISBN_PATTERN = re.compile(r"^(?:\d{9}[\dX]|\d{13})$")


class Book(BaseModel):
    title: str
    author: str
    isbn: str
    cost_usd: Decimal
    stock_quantity: int
    category: str
    supplier_country: str
    id: int | None = None
    selling_price_local: Decimal | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("isbn")
    @classmethod
    def _validate_isbn(cls, raw_isbn: str) -> str:
        normalized_isbn = re.sub(r"[\s-]", "", raw_isbn).upper()
        if not _ISBN_PATTERN.match(normalized_isbn):
            raise InvalidBookData("El ISBN debe tener 10 o 13 dígitos")
        return normalized_isbn

    @field_validator("cost_usd")
    @classmethod
    def _validate_cost_usd(cls, cost_usd: Decimal) -> Decimal:
        if cost_usd <= 0:
            raise InvalidBookData("cost_usd debe ser mayor a 0")
        return cost_usd

    @field_validator("stock_quantity")
    @classmethod
    def _validate_stock_quantity(cls, stock_quantity: int) -> int:
        if stock_quantity < 0:
            raise InvalidBookData("stock_quantity no puede ser negativo")
        return stock_quantity

    def with_changes(self, changes: dict[str, Any]) -> "Book":
        # se reconstruye para revalidar: model_copy(update=...) se saltea los validadores
        return Book(**{**self.model_dump(), **changes})
