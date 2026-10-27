"""JSON schemas for the Personio streams."""

from singer_sdk.typing import (
    ArrayType,
    DateTimeType,
    IntegerType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

persons_schema = PropertiesList(
    Property("id", StringType),
    Property("email", StringType),
    Property("created_at", DateTimeType),
    Property("updated_at", DateTimeType),
    Property("first_name", StringType),
    Property("last_name", StringType),
    Property("preferred_name", StringType),
    Property("gender", StringType),
    Property(
        "profile_picture",
        ObjectType(
            Property("url", StringType),
        ),
    ),
    Property("status", StringType),
    Property(
        "custom_attributes",
        ArrayType(
            ObjectType(
                Property("id", StringType),
                Property("type", StringType),
                Property("value", StringType),
                Property("global_id", StringType),
            )
        ),
    ),
    Property(
        "employments",
        ArrayType(
            ObjectType(
                Property("id", StringType),
            )
        ),
    ),
    Property(
        "_meta",
        ObjectType(
            Property(
                "links",
                ObjectType(
                    Property(
                        "employments",
                        ObjectType(
                            Property("href", StringType),
                        ),
                    )
                ),
            )
        ),
    ),
).to_dict()

employments_schema = PropertiesList(
    Property("id", StringType),
    Property("status", StringType),
    Property("weekly_working_hours", IntegerType),
    Property("probation_end_date", DateTimeType),
    Property("employment_start_date", DateTimeType),
    Property("full_time_weekly_working_hours", IntegerType),
    Property("employment_end_date", DateTimeType),
    Property("type", StringType),
    Property("contract_end_date", DateTimeType),
    Property("created_at", DateTimeType),
    Property("updated_at", DateTimeType),
    Property(
        "position",
        ObjectType(
            Property("title", StringType),
        ),
    ),
    Property(
        "supervisor",
        ObjectType(
            Property("id", StringType),
        ),
    ),
    Property(
        "office",
        ObjectType(
            Property("id", StringType),
        ),
    ),
    Property(
        "legal_entity",
        ObjectType(
            Property("id", StringType),
        ),
    ),
    Property(
        "sub_company",
        ObjectType(
            Property("id", StringType),
        ),
    ),
    Property(
        "org_units",
        ArrayType(
            ObjectType(
                Property("type", StringType),
                Property("id", StringType),
            )
        ),
    ),
    Property(
        "cost_centers",
        ArrayType(
            ObjectType(
                Property("id", StringType),
                Property("weight", IntegerType),
            )
        ),
    ),
    Property(
        "person",
        ObjectType(
            Property("id", StringType),
        ),
    ),
    Property(
        "termination",
        ObjectType(
            Property("termination_date", DateTimeType),
            Property("last_working_date", DateTimeType),
            Property("terminated_at", DateTimeType),
            Property("type", StringType),
            Property("reason", StringType),
        ),
    ),
    Property(
        "_meta",
        ObjectType(
            Property(
                "links",
                ObjectType(
                    Property(
                        "person",
                        ObjectType(
                            Property("href", StringType),
                        ),
                    ),
                    Property(
                        "supervisor",
                        ObjectType(
                            Property("href", StringType),
                        ),
                    ),
                ),
            ),
        ),
    ),
).to_dict()

org_units_schema = PropertiesList(
    Property("id", StringType),
    Property("name", StringType),
    Property("type", StringType),
    Property("abbreviation", StringType),
    Property("description", StringType),
    Property("resource_uri", StringType),
    Property("created_time", DateTimeType),
    Property(
        "_meta",
        ObjectType(
            Property(
                "links",
                ObjectType(
                    Property(
                        "self",
                        ObjectType(
                            Property("href", StringType),
                        ),
                    )
                ),
            ),
        ),
    ),
).to_dict()

custom_attributes_schema = PropertiesList(
    Property("key", StringType),
    Property("label", StringType),
    Property("type", StringType),
    Property("universal_id", StringType),
    Property("options", ArrayType(StringType)),
).to_dict()
