"""Shared test fixtures."""

import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def config_xml_bytes() -> bytes:
    """Load the real config_web.xml fixture."""
    return (FIXTURES_DIR / "config_web.xml").read_bytes()


@pytest.fixture
def config_no_r2_xml_bytes() -> bytes:
    """Load config_web.xml with R2 removed."""
    return (FIXTURES_DIR / "config_web_no_r2.xml").read_bytes()


@pytest.fixture
def new_arrivals_json() -> dict:
    """Load the new arrivals JSON fixture."""
    return json.loads((FIXTURES_DIR / "new_arrivals.json").read_text())


@pytest.fixture
def series_detail_json() -> dict:
    """Load the series detail JSON fixture."""
    return json.loads((FIXTURES_DIR / "series_detail.json").read_text())


@pytest.fixture
def live_programs_json() -> dict:
    """Load the live programs JSON fixture."""
    return json.loads((FIXTURES_DIR / "live_programs.json").read_text())

