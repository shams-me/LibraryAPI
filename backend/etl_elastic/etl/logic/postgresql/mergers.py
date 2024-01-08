from abc import (
    ABC,
    abstractmethod,
)
from functools import (
    lru_cache,
)
from itertools import (
    chain,
    zip_longest,
)
from typing import (
    Iterator,
    cast,
)

from psycopg2.extras import (
    DictCursor,
)

from etl.logic.storage.storage import (
    Storage,
)
from loguru import (
    logger,
)
from psycopg2._psycopg import (
    connection as pg_connection,
)


class MergerInt(ABC):
    @abstractmethod
    def merge(
        self,
        connection: pg_connection,
    ) -> Iterator[None]:
        ...


class BaseMerger(MergerInt):
    input_topic: str
    output_topic: str
    table: str
    storage = Storage()
    batch_size = 50

    def get_query(
        self,
    ) -> str:
        raise NotImplementedError

    def merge(
        self,
        connection: pg_connection,
    ) -> Iterator[None]:
        query = self.get_query()
        item_ids = self.storage.get(self.input_topic)

        if not item_ids:
            return iter([])

        unique_ids = tuple(set(chain(*item_ids)))
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                query,
                vars=(unique_ids,),
            )
            while item_data := cursor.fetchmany(size=self.batch_size):
                logger.debug(f"Retrieved {len(item_data)} rows from `{self.table}` table")
                self.storage.set_value(
                    self.output_topic,
                    item_data,
                )
                yield None


class BooksMerger(BaseMerger):
    input_topic = "book_ids"
    output_topic = "books_sql_data"

    table = "public.books"

    def get_query(
        self,
    ) -> str:
        query = f"""
    SELECT
        b.id, b.title, b.description, b.language, b.isbn, 
        b.publication_date, b.created_at, b.modified_at,
        COALESCE (
            JSON_AGG(
                DISTINCT jsonb_build_object(
                    'author_id', a.id,
                    'author_name', a.name || ' ' || a.last_name
                )
            ) FILTER (WHERE a.id IS NOT NULL),
            '[]'
        ) AS authors,
        COALESCE (
            JSON_AGG(
                DISTINCT jsonb_build_object(
                    'category_id', c.id,
                    'category_name', c.name,
                    'category_description', c.description
                )
            ) FILTER (WHERE c.id IS NOT NULL),
            '[]'
        ) AS categories
    FROM {self.table} AS b
    LEFT JOIN public.books_authors ba ON ba.book_id = b.id
    LEFT JOIN public.authors a ON a.id = ba.author_id
    LEFT JOIN public.books_categories bc ON bc.book_id = b.id
    LEFT JOIN public.categories c ON c.id = bc.category_id
    WHERE b.id IN %s
    GROUP BY b.id
    ORDER BY b.modified_at
    ;
    """
        return query


class AuthorsMerger(BaseMerger):
    input_topic = "author_ids"
    output_topic = "authors_sql_data"

    table = "public.authors"

    def get_query(
        self,
    ) -> str:
        query = f"""
        SELECT id, name, last_name, biography, created_at, modified_at
        FROM {self.table}
        WHERE id IN %s 
        ORDER BY modified_at
        ;
        """
        return query


class CategoriesMerger(BaseMerger):
    input_topic = "category_ids"
    output_topic = "categories_sql_data"

    table = "public.categories"

    def get_query(
        self,
    ) -> str:
        query = f"""
        SELECT id, name, description, created_at, modified_at
        FROM {self.table}
        WHERE id IN %s
        ORDER BY modified_at
        ;
        """
        return query


@lru_cache
def get_mergers() -> list[MergerInt]:
    mergers = [merger() for merger in BaseMerger.__subclasses__()]
    return cast(
        list[MergerInt],
        mergers,
    )


def run_mergers(
    connection: pg_connection,
) -> Iterator[None]:
    mergers = get_mergers()
    yield from zip_longest(*[merger.merge(connection) for merger in mergers])
