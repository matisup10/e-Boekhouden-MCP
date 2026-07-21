"""Base service with HTTP logic for the e-Boekhouden SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator, TypeVar

import httpx

from eboekhouden.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    SecurityError,
    ValidationError,
)
from eboekhouden.filters import Filter, build_filter_params
from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse

if TYPE_CHECKING:
    from eboekhouden.client import EBoekhoudenClient


T = TypeVar("T", bound=EBoekhoudenModel)
P = TypeVar("P", bound=PaginatedResponse)


class BaseService:
    """Base service class with common HTTP methods."""

    def __init__(self, client: "EBoekhoudenClient"):
        self._client = client

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make an authenticated HTTP request."""
        self._client._ensure_session()
        response = self._client._ensure_http_client().request(
            method,
            path,
            json=json,
            params=params,
            headers={"Authorization": self._client._session_token},
        )
        self._handle_errors(response)
        return response

    def _handle_errors(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        if response.status_code < 400:
            return

        try:
            data = response.json()
        except Exception:
            data = {}

        code = data.get("code")
        title = data.get("title", "Unknown error")
        message = data.get("message", title)
        error_type = data.get("type")

        if response.status_code == 401:
            raise AuthenticationError(message, code)
        elif response.status_code == 403:
            security_type = data.get("securityType")
            raise SecurityError(message, code, security_type)
        elif response.status_code == 404:
            raise NotFoundError(message, code, data)
        elif response.status_code == 400:
            errors = data.get("errors", {})
            raise ValidationError(message, code, errors)
        else:
            raise APIError(message, response.status_code, code, error_type, data)

    def _get(self, path: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """Make a GET request."""
        return self._request("GET", path, params=params)

    def _post(self, path: str, json: dict[str, Any] | None = None) -> httpx.Response:
        """Make a POST request."""
        return self._request("POST", path, json=json)

    def _patch(self, path: str, json: dict[str, Any] | None = None) -> httpx.Response:
        """Make a PATCH request."""
        return self._request("PATCH", path, json=json)

    def _delete(self, path: str) -> httpx.Response:
        """Make a DELETE request."""
        return self._request("DELETE", path)

    def _build_params(
        self,
        limit: int | None = None,
        offset: int | None = None,
        filters: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, str]:
        """Build query parameters from common arguments and filters."""
        params: dict[str, str] = {}

        if limit is not None:
            params["limit"] = str(limit)
        if offset is not None:
            params["offset"] = str(offset)

        # Add raw kwargs
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, Filter):
                    k, v = value.to_param(key)
                    params[k] = v
                else:
                    params[key] = str(value)

        # Add filters dict
        if filters:
            params.update(build_filter_params(filters))

        return params

    def _model_to_dict(self, model: EBoekhoudenModel) -> dict[str, Any]:
        """Convert a Pydantic model to a dict for API request."""
        return model.model_dump(mode="json", by_alias=True, exclude_none=True)

    def _paginate(
        self,
        path: str,
        response_model: type[P],
        item_model: type[T],
        limit: int = 100,
        **kwargs: Any,
    ) -> Generator[T, None, None]:
        """Iterate through all pages of a paginated endpoint.

        Args:
            path: API endpoint path
            response_model: Paginated response model class
            item_model: Item model class
            limit: Items per page (max 2000)
            **kwargs: Additional filter parameters

        Yields:
            Individual items from all pages
        """
        offset = 0
        while True:
            params = self._build_params(limit=limit, offset=offset, **kwargs)
            response = self._get(path, params)
            data = response.json()
            result = response_model.model_validate(data)

            for item_data in data.get("items", []):
                yield item_model.model_validate(item_data)

            if len(result.items) < limit:
                break
            offset += limit
