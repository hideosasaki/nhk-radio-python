"""On-demand (聞き逃し) API client."""

from __future__ import annotations

from typing import Any

import aiohttp

from .const import ONDEMAND_NEW_ARRIVALS_URL, ONDEMAND_SERIES_URL, REQUEST_TIMEOUT
from .errors import ApiError, NetworkError
from .models import (
    OndemandCorner,
    OndemandEpisode,
    OndemandSeries,
    OndemandSeriesDetail,
)


async def fetch_new_arrivals(
    session: aiohttp.ClientSession,
) -> list[OndemandSeries]:
    """Fetch the new arrivals list."""
    try:
        async with session.get(
            ONDEMAND_NEW_ARRIVALS_URL,
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
        ) as resp:
            if resp.status != 200:
                raise ApiError(resp.status, ONDEMAND_NEW_ARRIVALS_URL)
            data = await resp.json()
    except aiohttp.ClientError as exc:
        raise NetworkError(ONDEMAND_NEW_ARRIVALS_URL) from exc

    return parse_new_arrivals(data)


async def fetch_series(
    session: aiohttp.ClientSession,
    site_id: str,
    corner_site_id: str,
) -> OndemandSeriesDetail:
    """Fetch episodes for a specific series corner."""
    params = {"site_id": site_id, "corner_site_id": corner_site_id}
    try:
        async with session.get(
            ONDEMAND_SERIES_URL,
            params=params,
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
        ) as resp:
            if resp.status != 200:
                raise ApiError(resp.status, ONDEMAND_SERIES_URL)
            data = await resp.json()
    except aiohttp.ClientError as exc:
        raise NetworkError(ONDEMAND_SERIES_URL) from exc

    return parse_series_detail(data)


def parse_new_arrivals(data: dict[str, Any]) -> list[OndemandSeries]:
    """Parse the new arrivals JSON response."""
    result: list[OndemandSeries] = []
    for item in data["corners"]:
        corner = OndemandCorner(
            corner_id=str(item["id"]),
            corner_site_id=item["corner_site_id"],
            title=item.get("corner_name", "") or item["title"],
            series_site_id=item["series_site_id"],
        )
        series = OndemandSeries(
            series_id=str(item["id"]),
            site_id=item["series_site_id"],
            title=item["title"],
            description="",
            radio_broadcast=item["radio_broadcast"],
            thumbnail_url=item.get("thumbnail_url"),
            corners=[corner],
        )
        result.append(series)
    return result


def parse_series_detail(data: dict[str, Any]) -> OndemandSeriesDetail:
    """Parse the series detail JSON response."""
    episodes: list[OndemandEpisode] = []
    for ep in data["episodes"]:
        episodes.append(
            OndemandEpisode(
                episode_id=str(ep["id"]),
                title=ep["program_title"],
                description=ep.get("program_sub_title", ""),
                stream_url=ep["stream_url"],
                onair_date=ep["onair_date"],
                closed_at=ep["closed_at"],
            )
        )

    return OndemandSeriesDetail(
        series_title=data["title"],
        corner_title=data.get("corner_name", ""),
        thumbnail_url=data.get("thumbnail_url"),
        episodes=episodes,
    )
