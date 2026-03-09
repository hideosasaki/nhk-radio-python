# nhk-radio-python-sdk

NHKラジオ（らじる★らじる）の配信URL取得のための非同期Python SDK。

## 機能

- **ライブストリーム** — 地域・チャンネル指定でHLS配信URLを取得
- **聞き逃し（オンデマンド）** — 番組の聞き逃し配信を検索・再生URLを取得

チャンネル構成は `config_web.xml` から動的に検出するため、NHKのチャンネル変更（R2廃止等）にも自動対応します。

## インストール

```bash
pip install nhk-radio-python-sdk
```

または開発用:

```bash
git clone https://github.com/sasaki/nhk-radio-python-sdk.git
cd nhk-radio-python-sdk
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 使い方

### 基本

```python
import asyncio
import aiohttp
from nhk_radio import NhkRadioClient

async def main():
    async with aiohttp.ClientSession() as session:
        client = NhkRadioClient(session, area="tokyo")

        # 利用可能なチャンネル一覧
        channels = await client.get_channels()
        for ch in channels:
            print(f"{ch.name}: {ch.stream_url}")

asyncio.run(main())
```

### ライブストリーム

```python
# 特定チャンネルの配信URLを取得
url = await client.get_stream_url("r1")  # NHKラジオ第1
url = await client.get_stream_url("fm")  # NHK-FM

# 全地域の一覧
areas = await client.get_areas()
for area in areas:
    print(f"{area.name} ({area.id}): {[ch.id for ch in area.channels]}")
```

利用可能な地域: `sapporo`, `sendai`, `tokyo`, `nagoya`, `osaka`, `hiroshima`, `matsuyama`, `fukuoka`

### 聞き逃し（オンデマンド）

```python
# 新着番組の一覧
series_list = await client.get_ondemand_new_arrivals()
for series in series_list:
    print(f"{series.title} ({series.site_id})")

# チャンネルで絞り込み
fm_series = await client.get_ondemand_new_arrivals(channel="fm")

# カスタムフィルタ（キーワード検索）
news = await client.get_ondemand_new_arrivals(
    filter_fn=lambda s: "ニュース" in s.title
)

# 正規表現
import re
pattern = re.compile(r"英語|英会話")
english = await client.get_ondemand_new_arrivals(
    filter_fn=lambda s: pattern.search(s.title) is not None
)

# 組み合わせ
fm_classic = await client.get_ondemand_new_arrivals(
    channel="fm",
    filter_fn=lambda s: "クラシック" in s.title,
)

# 番組のエピソード一覧と再生URL
detail = await client.get_ondemand_series(
    site_id=series_list[0].site_id,
    corner_site_id=series_list[0].corners[0].corner_site_id,
)
for ep in detail.episodes:
    print(f"  {ep.title}: {ep.stream_url}")
```

### 設定の再読み込み

NHKは配信URLを不定期に変更します。長時間稼働するアプリケーションでは定期的に設定を再取得してください。

```python
await client.refresh_config()
```

## Home Assistant Integration での利用

このSDKは Home Assistant Custom Integration から利用することを想定しています。

```python
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from nhk_radio import NhkRadioClient

async def async_setup_entry(hass, entry):
    session = async_get_clientsession(hass)
    client = NhkRadioClient(session, area=entry.data["area"])
    # client を使って media_player エンティティを構築
```

## エラーハンドリング

すべての例外は `NhkRadioError` を継承しています。

```python
from nhk_radio import NhkRadioError, ConfigFetchError, AreaNotFoundError, ChannelNotFoundError

try:
    url = await client.get_stream_url("r1")
except ConfigFetchError:
    # config_web.xml の取得・パースに失敗
    pass
except AreaNotFoundError as e:
    # 指定した地域が存在しない
    print(f"利用可能: {e.available}")
except ChannelNotFoundError as e:
    # 指定したチャンネルが存在しない
    print(f"利用可能: {e.available}")
except NhkRadioError:
    # その他のSDKエラー
    pass
```

## 開発

```bash
# テスト
pytest -v

# 型チェック
mypy nhk_radio

# リント
ruff check nhk_radio
```

## ライセンス

Apache License 2.0
