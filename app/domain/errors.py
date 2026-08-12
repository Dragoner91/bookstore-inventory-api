class DomainError(Exception):
    """Error de negocio. La capa API lo traduce al status HTTP que corresponda."""


class BookNotFound(DomainError):
    pass


class DuplicateISBN(DomainError):
    pass


class InvalidBookData(DomainError):
    pass
