"""Tests for live.py."""

import pytest

from nhk_radio.config import parse_config
from nhk_radio.errors import AreaNotFoundError, ChannelNotFoundError
from nhk_radio.live import get_areas, get_channels_for_area, get_stream_url


@pytest.fixture
def config(config_xml_bytes: bytes):
    return parse_config(config_xml_bytes)


def test_get_areas(config) -> None:
    areas = get_areas(config)
    assert len(areas) == 8
    area_ids = {a.id for a in areas}
    assert "tokyo" in area_ids


def test_get_channels_for_area(config) -> None:
    channels = get_channels_for_area(config, "tokyo")
    assert len(channels) == 3
    assert any(ch.id == "r1" for ch in channels)


def test_get_channels_for_area_invalid(config) -> None:
    with pytest.raises(AreaNotFoundError) as exc_info:
        get_channels_for_area(config, "invalid")
    assert "invalid" in str(exc_info.value)
    assert exc_info.value.available


def test_get_stream_url(config) -> None:
    url = get_stream_url(config, "tokyo", "r1")
    assert url.endswith(".m3u8")


def test_get_stream_url_invalid_channel(config) -> None:
    with pytest.raises(ChannelNotFoundError) as exc_info:
        get_stream_url(config, "tokyo", "invalid")
    assert exc_info.value.available


def test_get_stream_url_invalid_area(config) -> None:
    with pytest.raises(AreaNotFoundError):
        get_stream_url(config, "invalid", "r1")
