"""Stream type classes for tap-personio."""

from __future__ import annotations

import typing as t

from singer_sdk.exceptions import FatalAPIError

from tap_personio.client import PersonioStream
from tap_personio.schemas import (
    custom_attributes_schema,
    employments_schema,
    org_units_schema,
    persons_schema,
)

if t.TYPE_CHECKING:
    from singer_sdk.helpers import types


class PersonsStream(PersonioStream):
    """Stream for Personio persons endpoint."""

    name = "persons"
    path = "/persons"
    primary_keys = ("id",)
    schema = persons_schema

    def get_child_context(
        self,
        record: types.Record,
        context: types.Context | None,  # noqa: ARG002
    ) -> types.Context:
        """Return a context dictionary for child streams."""
        return {
            "person_id": record["id"],
        }


class EmploymentsStream(PersonioStream):
    """Stream for Personio employments endpoint."""

    name = "employments"
    path = "/persons/{person_id}/employments"
    parent_stream_type = PersonsStream
    primary_keys = ("id",)
    schema = employments_schema
    state_partitioning_keys = []  # noqa: RUF012

    def generate_child_contexts(
        self,
        record: types.Record,
        context: types.Context | None,  # noqa: ARG002
    ) -> t.Iterable[types.Context | None]:
        """Generate child contexts.

        Args:
            record: Individual record in the stream.
            context: Stream partition or context dictionary.

        Yields:
            A child context for each child stream.
        """
        org_units = record.get("org_units")
        if not org_units:
            return
        for org_unit in org_units:
            yield {"org_unit_id": org_unit["id"], "org_unit_type": org_unit["type"]}


class OrgUnitsStream(PersonioStream):
    """Stream for Personio org units endpoint."""

    name = "org_units"
    path = "/org-units/{org_unit_id}"
    parent_stream_type = EmploymentsStream
    primary_keys = ("id",)
    schema = org_units_schema
    records_jsonpath = "$"

    @property
    def visited_units(self) -> set[str]:
        """Set of already visited org unit IDs to prevent duplicates."""
        if not hasattr(self, "_visited_units"):
            self._visited_units: set[str] = set()
        return self._visited_units

    def get_records(self, context: types.Context | None) -> t.Iterable[dict[str, t.Any]]:
        """Return a generator of record-type dictionary objects.

        Each record emitted should be a dictionary of property names to their values.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            One item per (possibly processed) record in the API.
        """
        if context is None:
            return
        org_unit_id: str = context["org_unit_id"]
        if org_unit_id in self.visited_units:
            self.logger.info("Skipping already visited org unit ID: %s", org_unit_id)
            return
        self.visited_units.add(org_unit_id)
        try:
            records = list(self.request_records(context))
            self.logger.info(records)
            yield from records
        except FatalAPIError as e:
            self.logger.warning(e)
            return

    def get_url_params(
        self,
        context: types.Context | None,
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params = super().get_url_params(context, next_page_token)
        params["type"] = (context or {}).get("org_unit_type")
        return params


class CustomAttributesStream(PersonioStream):
    """Stream for Personio custom attributes endpoint."""

    name = "custom_attributes"
    path = ""
    schema = custom_attributes_schema
    primary_keys = ("key",)
    records_jsonpath = "$.data[*]"

    def get_url(self, context: types.Context | None) -> str:  # noqa: ARG002
        """Return the URL for the stream, potentially using context.

        Args:
            context: Stream partition or context dictionary.

        Returns:
            The URL for the stream.
        """
        return "http://api.personio.de/v1/company/employees/custom-attributes"
