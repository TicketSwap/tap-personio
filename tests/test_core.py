"""Tests standard tap features using the built-in SDK tests library."""

import datetime as dt

from singer_sdk.testing import get_tap_test_class

from tap_personio.tap import TapPersonio

SAMPLE_CONFIG = {
    "start_date": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
}


# Run standard built-in tap tests from the SDK:
TestTapPersonio = get_tap_test_class(
    tap_class=TapPersonio,
    config=SAMPLE_CONFIG,
)
