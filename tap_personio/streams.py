"""Stream type classes for tap-personio."""

from __future__ import annotations

import typing as t

from singer_sdk.exceptions import FatalAPIError
from singer_sdk.helpers import types

from tap_personio.client import PersonioStream
from tap_personio.schemas import employments_schema, org_units_schema, persons_schema


class PersonsStream(PersonioStream):
    """Define custom stream."""

    name = "persons"
    path = "/persons"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    schema = persons_schema

    def get_child_context(self, record: dict, context: dict | None) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "person_id": record["id"],
        }


class EmploymentsStream(PersonioStream):
    """Define custom stream."""

    name = "employments"
    path = "/persons/{person_id}/employments"
    parent_stream_type = PersonsStream
    primary_keys: t.ClassVar[list[str]] = ["id"]
    schema = employments_schema
    state_partitioning_keys = []

    def generate_child_contexts(
        self,
        record: types.Record,
        context: types.Context | None,
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
    """Define custom stream."""

    name = "org_units"
    path = "/org-units/{org_unit_id}"
    parent_stream_type = EmploymentsStream
    primary_keys: t.ClassVar[list[str]] = ["id"]
    schema = org_units_schema
    records_jsonpath = "$"

    @property
    def visited_units(self) -> set[str]:
        """Set of already visited org unit IDs to prevent duplicates."""
        if not hasattr(self, "_visited_units"):
            self._visited_units = set()
        return self._visited_units

    def get_records(self, context: dict) -> t.Iterable[dict[str, t.Any]]:
        """Return a generator of record-type dictionary objects.

        Each record emitted should be a dictionary of property names to their values.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            One item per (possibly processed) record in the API.
        """
        org_unit_id: str = context["org_unit_id"]
        if org_unit_id in self.visited_units:
            self.logger.info(f"Skipping already visited org unit ID: {org_unit_id}")
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
        context: dict,
        next_page_token: t.Any | None,
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params = super().get_url_params(context, next_page_token)
        params["type"] = context.get("org_unit_type")
        return params
