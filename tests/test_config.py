"""Tests for config.py parsing."""

import pytest

from nhk_radio.config import parse_config
from nhk_radio.errors import ConfigFetchError


def test_parse_config_standard(config_xml_bytes: bytes) -> None:
    """All 8 areas with 3 channels each should be parsed."""
    config = parse_config(config_xml_bytes)

    assert len(config.areas) == 8
    assert "tokyo" in config.areas
    assert "osaka" in config.areas
    assert "sapporo" in config.areas

    tokyo = config.areas["tokyo"]
    assert tokyo.name == "東京"
    assert len(tokyo.channels) == 3

    channel_ids = {ch.id for ch in tokyo.channels}
    assert channel_ids == {"r1", "r2", "fm"}

    # Verify stream URLs are populated
    for ch in tokyo.channels:
        assert ch.stream_url.startswith("https://")
        assert ch.stream_url.endswith(".m3u8")


def test_parse_config_channel_names(config_xml_bytes: bytes) -> None:
    """Channel display names should be correct."""
    config = parse_config(config_xml_bytes)
    tokyo = config.areas["tokyo"]

    names = {ch.id: ch.name for ch in tokyo.channels}
    assert names == {"r1": "R1", "r2": "R2", "fm": "FM"}


def test_parse_config_r2_shared(config_xml_bytes: bytes) -> None:
    """R2 should use the same stream URL across all areas."""
    config = parse_config(config_xml_bytes)
    r2_urls = set()
    for area in config.areas.values():
        r2 = area.get_channel("r2")
        if r2:
            r2_urls.add(r2.stream_url)
    assert len(r2_urls) == 1


def test_parse_config_no_r2(config_no_r2_xml_bytes: bytes) -> None:
    """When R2 is removed from XML, only R1 and FM should appear."""
    config = parse_config(config_no_r2_xml_bytes)

    assert len(config.areas) == 2
    tokyo = config.areas["tokyo"]
    channel_ids = {ch.id for ch in tokyo.channels}
    assert channel_ids == {"r1", "fm"}
    assert tokyo.get_channel("r2") is None


def test_parse_config_empty_xml() -> None:
    """Empty or invalid XML should raise ConfigFetchError."""
    with pytest.raises(ConfigFetchError):
        parse_config(b"<radiru_config><stream_url></stream_url></radiru_config>")


def test_parse_config_missing_stream_url() -> None:
    """Missing stream_url element should raise ConfigFetchError."""
    with pytest.raises(ConfigFetchError):
        parse_config(b"<radiru_config></radiru_config>")
