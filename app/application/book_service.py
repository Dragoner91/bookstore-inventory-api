from typing import Any

from app.domain.book import Book
from app.domain.errors import BookNotFound
from app.domain.ports import BookRepository


class BookService:
    def __init__(self, repository: BookRepository) -> None:
        self._repository = repository

    async def create(self, book: Book) -> Book:
        return await self._repository.add(book)

    async def get(self, book_id: int) -> Book:
        book = await self._repository.get(book_id)
        if book is None:
            raise BookNotFound(f"No existe un libro con id {book_id}")
        return book

    async def list_books(self, limit: int, offset: int) -> list[Book]:
        return await self._repository.list_books(limit, offset)

    async def update(self, book_id: int, changes: dict[str, Any]) -> Book:
        book = await self.get(book_id)
        return await self._repository.update(book.with_changes(changes))

    async def delete(self, book_id: int) -> None:
        if not await self._repository.delete(book_id):
            raise BookNotFound(f"No existe un libro con id {book_id}")

    async def find_by_category(self, category: str) -> list[Book]:
        return await self._repository.find_by_category(category)

    async def find_low_stock(self, threshold: int) -> list[Book]:
        return await self._repository.find_low_stock(threshold)
