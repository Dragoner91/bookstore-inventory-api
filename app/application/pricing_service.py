from decimal import Decimal

from app.domain.errors import BookNotFound
from app.domain.ports import BookRepository, ExchangeRateProvider
from app.domain.price import RATE_CURRENCY_CODE, PriceCalculation, calculate_price


class PricingService:
    def __init__(
        self,
        repository: BookRepository,
        exchange_provider: ExchangeRateProvider,
        margin_percentage: Decimal,
    ) -> None:
        self._repository = repository
        self._exchange_provider = exchange_provider
        self._margin_percentage = margin_percentage

    async def calculate(self, book_id: int) -> PriceCalculation:
        book = await self._repository.get(book_id)
        if book is None:
            raise BookNotFound(f"No existe un libro con id {book_id}")

        exchange_rate = await self._exchange_provider.get_rate(RATE_CURRENCY_CODE)
        calculation = calculate_price(book, exchange_rate, self._margin_percentage)

        book.selling_price_local = calculation.selling_price_local
        await self._repository.update(book)
        return calculation
