from abc import ABC, abstractmethod

from app.domain.book import Book
from app.domain.price import ExchangeRate


class BookRepository(ABC):
    @abstractmethod
    async def add(self, book: Book) -> Book:
        """Persiste un libro nuevo. Lanza DuplicateISBN si el ISBN ya existe."""

    @abstractmethod
    async def get(self, book_id: int) -> Book | None:
        """Devuelve el libro, o None si no existe."""

    @abstractmethod
    async def list_books(self, limit: int, offset: int) -> list[Book]:
        """Lista libros paginados, ordenados por id."""

    @abstractmethod
    async def update(self, book: Book) -> Book:
        """Actualiza un libro existente. Lanza DuplicateISBN si el ISBN choca con otro."""

    @abstractmethod
    async def delete(self, book_id: int) -> bool:
        """Elimina el libro. Devuelve False si no existía."""

    @abstractmethod
    async def find_by_category(self, category: str) -> list[Book]:
        """Libros de una categoría."""

    @abstractmethod
    async def find_low_stock(self, threshold: int) -> list[Book]:
        """Libros con stock estrictamente por debajo del umbral."""


class ExchangeRateProvider(ABC):
    @abstractmethod
    async def get_rate(self, currency_code: str) -> ExchangeRate:
        """Tasa USD → currency_code. No propaga fallos: ante error devuelve la tasa por defecto."""
