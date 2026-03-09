"""NHK Radio (らじる★らじる) Python SDK."""

from .client import NhkRadioClient
from .errors import (
    ApiError,
    AreaNotFoundError,
    ChannelNotFoundError,
    ConfigFetchError,
    NetworkError,
    NhkRadioError,
)
from .models import (
    Area,
    Channel,
    OndemandCorner,
    OndemandEpisode,
    OndemandSeries,
    OndemandSeriesDetail,
)

__all__ = [
    "ApiError",
    "Area",
    "AreaNotFoundError",
    "Channel",
    "ChannelNotFoundError",
    "ConfigFetchError",
    "NetworkError",
    "NhkRadioClient",
    "NhkRadioError",
    "OndemandCorner",
    "OndemandEpisode",
    "OndemandSeries",
    "OndemandSeriesDetail",
]
