"""Live stream URL resolution."""

from __future__ import annotations

from .config import RadiruConfig
from .errors import AreaNotFoundError, ChannelNotFoundError
from .models import Area, Channel


def get_areas(config: RadiruConfig) -> list[Area]:
    """Return all available areas."""
    return list(config.areas.values())


def get_channels_for_area(config: RadiruConfig, area_id: str) -> list[Channel]:
    """Return channels for an area."""
    area = config.areas.get(area_id)
    if area is None:
        raise AreaNotFoundError(area_id, list(config.areas.keys()))
    return area.channels


def get_stream_url(config: RadiruConfig, area_id: str, channel_id: str) -> str:
    """Return HLS URL for a specific channel in an area."""
    area = config.areas.get(area_id)
    if area is None:
        raise AreaNotFoundError(area_id, list(config.areas.keys()))
    channel = area.get_channel(channel_id)
    if channel is None:
        available = [ch.id for ch in area.channels]
        raise ChannelNotFoundError(channel_id, available)
    return channel.stream_url
