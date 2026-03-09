"""Tests for client.py with mocked HTTP."""

import pytest
from aioresponses import aioresponses
import aiohttp

from nhk_radio.client import NhkRadioClient
from nhk_radio.const import CONFIG_URL
from nhk_radio.errors import AreaNotFoundError, ChannelNotFoundError, ConfigFetchError


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
async def test_get_stream_url(mock_aiohttp, config_xml_bytes: bytes) -> None:
    mock_aiohttp.get(CONFIG_URL, body=config_xml_bytes)

    async with aiohttp.ClientSession() as session:
        client = NhkRadioClient(session, area="tokyo")
        url = await client.get_stream_url("r1")
        assert url.endswith(".m3u8")


@pytest.mark.asyncio
async def test_invalid_channel(mock_aiohttp, config_xml_bytes: bytes) -> None:
    mock_aiohttp.get(CONFIG_URL, body=config_xml_bytes)

    async with aiohttp.ClientSession() as session:
        client = NhkRadioClient(session, area="tokyo")
        with pytest.raises(ChannelNotFoundError):
            await client.get_stream_url("invalid")


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
