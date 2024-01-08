from enum import StrEnum, auto, unique


@unique
class ServiceInternalPermission(StrEnum):
    read = auto()
    update = auto()
    create = auto()
    delete = auto()
    blocked = auto()


@unique
class ServiceInternalActions(StrEnum):
    read = auto()
    update = auto()
    create = auto()
    delete = auto()


@unique
class ServiceInternalSrc(StrEnum):
    users = auto()
    permissions = auto()
    roles = auto()
    books = auto()
    authors = auto()
    categories = auto()
    books_categories = auto()
    books_authors = auto()


@unique
class ServiceInternalRoles(StrEnum):
    superadmin = auto()
    admin = auto()
    librarian = auto()
    membership = auto()
    guest = auto()
