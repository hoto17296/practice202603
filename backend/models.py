from typing import TypedDict


class HTTPExceptionBody[T = None](TypedDict):
    detail: T
