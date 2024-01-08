from enum import StrEnum, auto, unique


@unique
class ServiceInternalPermission(StrEnum):
    read = "READ"
    update = "UPDATE"
    create = "CREATE"
    delete = "DELETE"
    blocked = "BLOCKED"


@unique
class ServiceInternalActions(StrEnum):
    READ = auto()
    UPDATE = auto()
    CREATE = auto()
    DELETE = auto()


@unique
class ServiceInternalSrc(StrEnum):
    users = auto()
    permissions = auto()
    roles = auto()
    books = auto()
    authors = auto()
    categories = auto()


@unique
class ServiceInternalRoles(StrEnum):
    superadmin = auto()
    admin = auto()
    librarian = auto()
    membership = auto()
    guest = auto()
