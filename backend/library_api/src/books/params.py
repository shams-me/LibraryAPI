from enum import Enum
from typing import Annotated, Any

from fastapi import (
    Query,
)

from src.common.dependencies import (
    SortRequestParams,
    PaginationRequestParams,
    FilterRequestParams,
    FullTextSearchParams,
    META_INFO,
    CommonOrderByParams,
)


class BookSortOptions(str, Enum):
    LANGUAGE: str = "language"


class BookFilterOptions(str, Enum):
    AUTHOR_ID: str = "author_id"
    CATEGORY_ID: str = "category_id"


class BookRequestParams(
    SortRequestParams, PaginationRequestParams, FilterRequestParams, FullTextSearchParams
):
    SORT_ES_MAPPING = {BookSortOptions.LANGUAGE: BookSortOptions.LANGUAGE.value}

    sort_by: Annotated[
        BookSortOptions, Query(title=META_INFO.sort_by.title, description=META_INFO.sort_by.description)
    ] = BookSortOptions.LANGUAGE
    order_by: Annotated[
        CommonOrderByParams, Query(title=META_INFO.order_by.title, description=META_INFO.order_by.description)
    ] = CommonOrderByParams.DESC

    filter_by: Annotated[
        BookFilterOptions | None,
        Query(title=META_INFO.filter_by.title, description=META_INFO.filter_by.description),
    ] = None

    def to_es_params(
        self,
    ) -> dict[str, Any,]:
        pagination_params = PaginationRequestParams.to_es_params(self)
        sort_params = SortRequestParams.to_es_params(self)
        full_text_params = FullTextSearchParams.to_es_params(self)
        filter_params = FilterRequestParams.to_es_params(self)

        params = {
            **pagination_params,
            **sort_params,
        }
        if full_text_params or filter_params:
            params["query"] = {
                "bool": {
                    **full_text_params,
                    **filter_params,
                }
            }
        return params

    def es_filter_by_author_id(
        self,
    ) -> dict[str, Any,]:
        filter_subquery = {
            "filter": {
                "nested": {
                    "path": "authors",
                    "query": {"term": {"authors.id": self.filter_value}},
                }
            },
        }
        return filter_subquery

    def es_filter_by_category_id(
        self,
    ) -> dict[str, Any,]:
        filter_subquery = {
            "filter": {
                "nested": {
                    "path": "categories",
                    "query": {"term": {"categories.id": self.filter_value}},
                }
            },
        }
        return filter_subquery
