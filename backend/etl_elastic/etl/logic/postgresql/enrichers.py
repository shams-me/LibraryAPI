from abc import (
    ABC,
    abstractmethod,
)
from functools import (
    lru_cache,
)
from itertools import (
    chain,
)
from typing import (
    cast,
)
from uuid import (
    UUID,
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


class EnricherInt(ABC):
    @abstractmethod
    def enrich(
        self,
        connection: pg_connection,
    ) -> None:
        ...


class BaseEnricher(EnricherInt):
    input_topic: str
    output_topic: str

    storage = Storage()

    id_field: str | None = None
    join_table_name: str | None = None
    join_on_field: str | None = None

    def get_query(
        self,
    ) -> str:
        query = f"""
        SELECT DISTINCT b.id, b.modified_at
        FROM public.books AS b
        LEFT JOIN {self.join_table_name} ON
        {self.join_table_name}.{self.join_on_field} = b.id
        WHERE {self.join_table_name}.{self.id_field} IN %s
        ORDER BY b.modified_at;
        """
        return query

    def enrich(
        self,
        connection: pg_connection,
    ) -> None:
        logger.debug("Getting all modified books ids from the last checkup")

        producer_ids: list[list[UUID]] = self.storage.get(self.input_topic)
        if not producer_ids:
            return

        flat_ids = tuple(chain(*producer_ids))
        query = self.get_query()
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                vars=(flat_ids,),
            )
            enriched_ids = [res[0] for res in cursor.fetchall()]  # Assuming id is the first column

        self.storage.set_value(
            self.output_topic,
            enriched_ids,
        )


class AuthorBookEnricher(BaseEnricher):
    input_topic = "author_ids"
    output_topic = "book_ids"

    id_field = "author_id"
    join_table_name = "public.books_authors"
    join_on_field = "book_id"


class CategoryEnricher(BaseEnricher):
    input_topic = "category_ids"
    output_topic = "book_ids"

    id_field = "category_id"
    join_table_name = "public.books_categories"
    join_on_field = "book_id"


@lru_cache
def get_enrichers() -> list[EnricherInt]:
    enrichers = [enricher() for enricher in BaseEnricher.__subclasses__()]
    return cast(
        list[EnricherInt],
        enrichers,
    )


def run_enrichers(
    connection: pg_connection,
) -> None:
    for enricher in get_enrichers():
        enricher.enrich(connection)
