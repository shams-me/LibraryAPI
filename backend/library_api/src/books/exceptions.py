from src.common.exceptions import ResourceNotFound, ResourceConflict, BadRequest


class BookNotFound(ResourceNotFound):
    resource_name = "Book"


class BookCategoryExists(ResourceConflict):
    resource_name = "Book-Category"


class BookAuthorExists(ResourceConflict):
    resource_name = "Book-Author"


class BookCategoryBadRequest(BadRequest):
    source = "Book"
    relation = "Category"


class BookAuthorBadRequest(BadRequest):
    source = "Book"
    relation = "Author"
