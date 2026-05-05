from datetime import UTC, datetime
from typing import Annotated, TypedDict

from pydantic import PlainSerializer


class HTTPExceptionBody[T = None](TypedDict):
    detail: T


# API レスポンスで datetime を返す際に使用する型
# datetime (without timezone) データを UTC として扱い、Unix タイムスタンプ (秒) に変換して返す
UnixTimestamp = Annotated[
    datetime,
    PlainSerializer(lambda dt: dt.replace(tzinfo=UTC).timestamp(), return_type=float),
]
