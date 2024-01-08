from src.common.exceptions import ResourceNotFound


class CategoryNotFound(ResourceNotFound):
    resource_name = "Category"
