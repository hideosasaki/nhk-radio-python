"""Tests for client.py with mocked HTTP."""

from datetime import datetime, timedelta, timezone

import aiohttp
import pytest
from aioresponses import aioresponses

from nhk_radio.client import NhkRadioClient
from nhk_radio.const import CONFIG_URL, NOA_API_URL
from nhk_radio.errors import AreaNotFoundError, ConfigFetchError
from nhk_radio.models import Area, Channel, LiveInfo, LiveProgram

JST = timezone(timedelta(hours=9))


@pytest.fixture
def mock_aiohttp():
    with aioresponses() as m:
        yield m


@pytest.mark.asyncio
async def test_lazy_config_load(mock_aiohttp, config_xml_bytes: bytes) -> None:
    """Config should not be fetched at construction time."""
    async with aiohttp.ClientSession() as session:
        client = NhkRadioClient(session, area="tokyo")
        # No request yet
        assert client._config is None

        mock_aiohttp.get(CONFIG_URL, body=config_xml_bytes)
        channels = await client.get_channels()
        assert len(channels) == 3
        assert client._config is not None


@pytest.mark.asyncio
async def test_invalid_area(mock_aiohttp, config_xml_bytes: bytes) -> None:
    mock_aiohttp.get(CONFIG_URL, body=config_xml_bytes)

    async with aiohttp.ClientSession() as session:
        client = NhkRadioClient(session, area="invalid")
        with pytest.raises(AreaNotFoundError):
            await client.get_channels()


@pytest.mark.asyncio
async def test_config_fetch_failure(mock_aiohttp) -> None:
    mock_aiohttp.get(CONFIG_URL, status=500)

    async with aiohttp.ClientSession() as session:
        client = NhkRadioClient(session, area="tokyo")
        with pytest.raises(ConfigFetchError):
            await client.get_channels()


# --- _inject_stream_url tests ---


def _make_live_program(**kwargs) -> LiveProgram:
    defaults = {
        "title": "Test",
        "description": "",
        "thumbnail_url": None,
        "series_name": "Test Series",
        "series_site_id": "XXXXX",
        "act": "",
        "channel_id": "r1",
        "stream_url": "",
        "start_at": datetime(2026, 1, 1, 12, 0, tzinfo=JST),
        "end_at": datetime(2026, 1, 1, 13, 0, tzinfo=JST),
        "event_id": "test-event",
    }
    defaults.update(kwargs)
    return LiveProgram(**defaults)


def test_inject_stream_url_fills_present() -> None:
    """_inject_stream_url should fill stream_url from channel."""
    channel = Channel(id="r1", name="R1", stream_url="https://example.com/r1.m3u8")
    area = Area(id="tokyo", name="東京", areakey="130", channels=[channel])
    info = LiveInfo(
        channel=channel,
        area=area,
        previous=None,
        present=_make_live_program(stream_url=""),
        following=None,
    )
    result = NhkRadioClient._inject_stream_url(info)
    assert result.present.stream_url == "https://example.com/r1.m3u8"


def test_inject_stream_url_fills_previous_and_following() -> None:
    """_inject_stream_url should fill all non-None programs."""
    channel = Channel(id="fm", name="FM", stream_url="https://example.com/fm.m3u8")
    area = Area(id="tokyo", name="東京", areakey="130", channels=[channel])
    info = LiveInfo(
        channel=channel,
        area=area,
        previous=_make_live_program(channel_id="fm", stream_url=""),
        present=_make_live_program(channel_id="fm", stream_url=""),
        following=_make_live_program(channel_id="fm", stream_url=""),
    )
    result = NhkRadioClient._inject_stream_url(info)
    assert result.previous.stream_url == "https://example.com/fm.m3u8"
    assert result.present.stream_url == "https://example.com/fm.m3u8"
    assert result.following.stream_url == "https://example.com/fm.m3u8"


@pytest.mark.asyncio
async def test_get_live_programs_injects_stream_url(
    mock_aiohttp, config_xml_bytes: bytes, live_programs_json: dict
) -> None:
    """get_live_programs should inject stream_url from config."""
    mock_aiohttp.get(CONFIG_URL, body=config_xml_bytes)
    mock_aiohttp.get(
        NOA_API_URL.format(areakey="130"),
        payload=live_programs_json,
    )

    async with aiohttp.ClientSession() as session:
        client = NhkRadioClient(session, area="tokyo")
        result = await client.get_live_programs()

        for info in result.values():
            assert info.present.stream_url != ""
            assert info.present.stream_url.endswith(".m3u8")
