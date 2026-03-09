"""Exception hierarchy for the nhk_radio SDK."""


class NhkRadioError(Exception):
    """Base exception for the nhk_radio SDK."""


class ConfigFetchError(NhkRadioError):
    """Failed to fetch or parse config_web.xml."""


class AreaNotFoundError(NhkRadioError):
    """The requested area is not in the config."""

    def __init__(self, area_id: str, available: list[str]) -> None:
        self.area_id = area_id
        self.available = available
        super().__init__(
            f"Area '{area_id}' not found. Available: {', '.join(available)}"
        )


class ChannelNotFoundError(NhkRadioError):
    """The requested channel is not available in the area."""

    def __init__(self, channel_id: str, available: list[str]) -> None:
        self.channel_id = channel_id
        self.available = available
        super().__init__(
            f"Channel '{channel_id}' not found. Available: {', '.join(available)}"
        )


class ApiError(NhkRadioError):
    """An API request failed."""

    def __init__(self, status: int, url: str) -> None:
        self.status = status
        self.url = url
        super().__init__(f"API request to {url} failed with status {status}")


class NetworkError(NhkRadioError):
    """A network connection failed."""

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"Network request to {url} failed")
