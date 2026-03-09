"""Tests for ondemand.py parsing."""

import aiohttp
import pytest
from aioresponses import aioresponses

from nhk_radio.const import ONDEMAND_NEW_ARRIVALS_URL
from nhk_radio.errors import NetworkError
from nhk_radio.ondemand import (
    fetch_new_arrivals,
    parse_new_arrivals,
    parse_series_detail,
)


def test_parse_new_arrivals(new_arrivals_json: dict) -> None:
    result = parse_new_arrivals(new_arrivals_json)
    assert len(result) > 0

    first = result[0]
    assert first.title
    assert first.site_id
    assert len(first.corners) == 1
    assert first.corners[0].corner_site_id


def test_parse_series_detail(series_detail_json: dict) -> None:
    result = parse_series_detail(series_detail_json)
    assert result.series_title
    assert result.thumbnail_url
    assert len(result.episodes) > 0

    ep = result.episodes[0]
    assert ep.title
    assert ep.stream_url.endswith(".m3u8")
    assert ep.episode_id
    assert ep.onair_date
    assert ep.closed_at
    # Fields inherited from parent
    assert ep.thumbnail_url == result.thumbnail_url
    assert ep.series_name == result.series_title
    assert ep.act is not None


def test_parse_new_arrivals_empty() -> None:
    result = parse_new_arrivals({"corners": []})
    assert result == []


def test_parse_series_detail_no_episodes() -> None:
    result = parse_series_detail({"title": "Test", "corner_name": "", "episodes": []})
    assert result.series_title == "Test"
    assert result.thumbnail_url is None
    assert result.episodes == []


@pytest.mark.asyncio
async def test_fetch_new_arrivals_connection_error() -> None:
    """Connection errors should raise NetworkError, not ApiError."""
    with aioresponses() as m:
        m.get(ONDEMAND_NEW_ARRIVALS_URL, exception=aiohttp.ClientError("timeout"))
        async with aiohttp.ClientSession() as session:
            with pytest.raises(NetworkError) as exc_info:
                await fetch_new_arrivals(session)
            assert exc_info.value.url == ONDEMAND_NEW_ARRIVALS_URL
