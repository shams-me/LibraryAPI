from src.common.exceptions import (
    ResourceNotFound,
)


class AuthorNotFound(ResourceNotFound):
    resource_name = "Author"
