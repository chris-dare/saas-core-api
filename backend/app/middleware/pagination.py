"""The :mod:`api.middleware.pagination` containts middleware for implementing custom pagination in this API"""

from typing import Generic, TypeVar

from fastapi_pagination.links import Page

T = TypeVar("T")


class JsonApiPage(Page[T], Generic[T]):
    """JSON:API 1.0 specification says that result key should be a `data`.
    Code copied from: https://uriyyo-fastapi-pagination.netlify.app/customization/
    """

    class Config:
        allow_population_by_field_name = True
        fields = {"items": {"alias": "data"}}
