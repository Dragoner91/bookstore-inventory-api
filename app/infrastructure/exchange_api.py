import logging
from decimal import Decimal, InvalidOperation

import httpx

from app.config import settings
from app.domain.ports import ExchangeRateProvider
from app.domain.price import ExchangeRate

logger = logging.getLogger(__name__)


class ExchangeRateApiProvider(ExchangeRateProvider):
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def get_rate(self, currency_code: str) -> ExchangeRate:
        try:
            response = await self._http_client.get(
                settings.exchange_api_url,
                timeout=settings.exchange_timeout_seconds,
            )
            response.raise_for_status()
            rate = Decimal(str(response.json()["rates"][currency_code]))
            return ExchangeRate(value=rate, source="api")
        except (httpx.HTTPError, KeyError, ValueError, InvalidOperation):
            # se capturan los tres fallos reales: red/timeout/5xx, moneda ausente
            # del payload, y valor no parseable
            logger.warning(
                "Fallo la API de tasas, se usa la tasa por defecto", exc_info=True
            )
            return ExchangeRate(
                value=settings.default_usd_rate,
                source="fallback",
                notice=(
                    "API de tasas no disponible; se usó la tasa por defecto "
                    f"DEFAULT_USD_RATE={settings.default_usd_rate}"
                ),
            )
