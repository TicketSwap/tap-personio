"""REST client handling, including PersonioStream base class."""

from __future__ import annotations

import sys
import typing as t
from functools import cached_property
from urllib.parse import parse_qsl

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta
from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk.streams import RESTStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    import requests
    from singer_sdk.helpers.types import Auth, Context


class PersonioAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for Personio."""

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the Personio API.

        Returns:
            A dict with the request body
        """
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }


class PersonioPaginator(BaseHATEOASPaginator):
    """A custom paginator class for Personio streams."""

    def get_next_url(self, response: requests.Response) -> str | None:
        """Override this method to extract a HATEOAS link from the response.

        Args:
            response: API response object.
        """
        return response.json().get("_meta", {}).get("links", {}).get("next", {}).get("href")


class PersonioStream(RESTStream):
    """Personio stream class."""

    # Update this value if necessary or override `parse_response`.
    records_jsonpath = "$._data[*]"

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return "https://api.personio.de/v2"

    @cached_property
    def authenticator(self) -> Auth:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return PersonioAuthenticator(
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            auth_endpoint=f"{self.url_base}/auth/token",
        )

    @override
    def get_new_paginator(self) -> PersonioPaginator:
        """Create a new pagination helper instance.

        Returns:
            A pagination helper instance, or ``None`` to indicate pagination
            is not supported.
        """
        return PersonioPaginator()

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any | None,
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {"limit": 50}
        if next_page_token:
            params.update(parse_qsl(next_page_token.query))
        starting_date = self.get_starting_timestamp(context)
        if starting_date:
            params["updated_at.gt"] = starting_date
        return params

    def post_process(
        self,
        row: dict,
        context: Context | None = None,  # noqa: ARG002
    ) -> dict:
        """As needed, append or transform raw data to match expected structure.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The processed record.
        """
        if "custom_attributes" in row:
            row["custom_attributes"] = [
                {
                    "global_id": attribute["global_id"],
                    "id": attribute["id"],
                    "type": attribute["type"],
                    "value": str(attribute["value"]),
                }
                for attribute in row["custom_attributes"]
            ]
        return row
