from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from pydantic import BaseModel

from app.domain.book import Book

RATE_CURRENCY_CODE = "VES"  # codigo ISO que se busca en la API de tasas
CURRENCY_LABEL = "Bs"  # como se muestra la moneda al cliente


class ExchangeRate(BaseModel):
    value: Decimal
    source: Literal["api", "fallback"]
    notice: str | None = None


class PriceCalculation(BaseModel):
    book_id: int
    cost_usd: Decimal
    exchange_rate: Decimal
    cost_local: Decimal
    margin_percentage: Decimal
    selling_price_local: Decimal
    currency: str
    rate_source: str
    rate_notice: str | None
    calculation_timestamp: datetime


def _round_to_cents(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_price(
    book: Book, exchange_rate: ExchangeRate,
    margin_percentage: Decimal
) -> PriceCalculation:
    # se redondea cost_local antes de aplicar el margen
    cost_local = _round_to_cents(book.cost_usd * exchange_rate.value)
    selling_price_local = _round_to_cents(cost_local * (1 + margin_percentage / 100))

    return PriceCalculation(
        book_id=book.id,
        cost_usd=book.cost_usd,
        exchange_rate=exchange_rate.value,
        cost_local=cost_local,
        margin_percentage=margin_percentage,
        selling_price_local=selling_price_local,
        currency=CURRENCY_LABEL,
        rate_source=exchange_rate.source,
        rate_notice=exchange_rate.notice,
        calculation_timestamp=datetime.now(timezone.utc),
    )
