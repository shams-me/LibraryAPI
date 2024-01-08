from abc import (
    ABC,
    abstractmethod,
)
from functools import (
    lru_cache,
)
from typing import (
    Type,
    cast,
)

from etl.logic.storage.storage import (
    Storage,
)
from .dataclasses import (
    SQLContainer,
    BookRow,
    AuthorRow,
    CategoryRow,
    ESBookDoc,
    ESAuthorDoc,
    ESCategoryDoc,
    BasicSQLRowDataInt,
)


class TransformerInt(ABC):
    dataclass: Type[SQLContainer]

    input_topic: str
    output_topic: str
    row = BasicSQLRowDataInt
    storage: Storage

    @abstractmethod
    def transform(
        self,
    ) -> None:
        ...


class BaseTransformer(TransformerInt):
    dataclass = SQLContainer
    storage = Storage()

    def transform(
        self,
    ) -> None:
        sql_data = self.storage.get(self.input_topic)
        if not sql_data:
            return

        sql_data = [self.row(**item) for item in sql_data[0]]
        es_data = self.dataclass(batch=sql_data)
        self.storage.set_value(
            self.output_topic,
            es_data.transform(),
        )


class BookTransformer(BaseTransformer):
    input_topic = "books_sql_data"
    output_topic = "books_es_data"
    row = BookRow
    dataclass = SQLContainer[
        BookRow,
        ESBookDoc,
    ]


class AuthorTransformer(BaseTransformer):
    input_topic = "authors_sql_data"
    output_topic = "authors_es_data"
    row = AuthorRow
    dataclass = SQLContainer[
        AuthorRow,
        ESAuthorDoc,
    ]


class CategoryTransformer(BaseTransformer):
    input_topic = "categories_sql_data"
    output_topic = "categories_es_data"
    row = CategoryRow
    dataclass = SQLContainer[
        CategoryRow,
        ESCategoryDoc,
    ]


@lru_cache
def get_transformers() -> list[TransformerInt]:
    transformers = [transformer() for transformer in BaseTransformer.__subclasses__()]
    return cast(
        list[TransformerInt],
        transformers,
    )


def run_transformers() -> None:
    for transformer in get_transformers():
        transformer.transform()
