from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from app.infrastructure.tables import BookTable, to_domain, to_table
from app.domain.book import Book
from app.domain.errors import DuplicateISBN
from app.domain.ports import BookRepository


class PostgresBookRepository(BookRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, book: Book) -> Book:
        row = to_table(book)
        self._session.add(row)
        await self._commit()
        await self._session.refresh(row)
        return to_domain(row)

    async def get(self, book_id: int) -> Book | None:
        row = await self._session.get(BookTable, book_id)
        return to_domain(row) if row else None

    async def list_books(self, limit: int, offset: int) -> list[Book]:
        return await self._fetch_books(
            select(BookTable).order_by(BookTable.id).limit(limit).offset(offset)
        )

    async def update(self, book: Book) -> Book:
        row = await self._session.get(BookTable, book.id)
        changes = book.model_dump(exclude={"id", "created_at", "updated_at"})
        for field_name, value in changes.items():
            setattr(row, field_name, value)
        await self._commit()
        await self._session.refresh(row)
        return to_domain(row)

    async def delete(self, book_id: int) -> bool:
        row = await self._session.get(BookTable, book_id)
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.commit()
        return True

    async def find_by_category(self, category: str) -> list[Book]:
        return await self._fetch_books(
            select(BookTable).where(BookTable.category == category)
        )

    async def find_low_stock(self, threshold: int) -> list[Book]:
        return await self._fetch_books(
            select(BookTable).where(BookTable.stock_quantity < threshold)
        )

    async def _fetch_books(self, statement: SelectOfScalar[BookTable]) -> list[Book]:
        rows = await self._session.exec(statement)
        return [to_domain(row) for row in rows]

    async def _commit(self) -> None:
        try:
            await self._session.commit()
        except IntegrityError as error:
            # el rollback es obligatorio: sin el, la sesion queda inutilizable
            await self._session.rollback()
            raise DuplicateISBN("Ya existe un libro con ese ISBN") from error
