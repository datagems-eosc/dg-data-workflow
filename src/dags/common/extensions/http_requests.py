import json
from http.cookiejar import CookieJar
from typing import Any, Iterable, Mapping, MutableMapping, Callable, TypeAlias, Protocol, TypeVar

import math
import requests
from requests import PreparedRequest, Response
from requests.auth import AuthBase

from common.enum.http_method import HttpMethod

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")
_T_co = TypeVar("_T_co", covariant=True)


class SupportsItems(Protocol[_KT, _VT]):
    def items(self) -> Iterable[tuple[_KT, _VT]]: ...


class SupportsRead(Protocol[_T_co]):
    def read(self, *args: Any, **kwargs: Any) -> _T_co: ...


HttpSupportsItems: TypeAlias = (SupportsItems[str | bytes | int | float, str | bytes | int | float | Iterable[
    str | bytes | int | float] | None] | tuple[str | bytes | int | float, str | bytes | int | float | Iterable[
    str | bytes | int | float] | None] | Iterable[tuple[str | bytes | int | float, str | bytes | int | float | Iterable[
    str | bytes | int | float] | None]] | str | bytes | None)
HttpData: TypeAlias = (Iterable[bytes] | str | bytes | SupportsRead[str | bytes] | list[tuple[Any, Any]] | tuple[
    tuple[Any, Any], ...] | Mapping[Any, Any] | None)
HttpHeaders: TypeAlias = (Mapping[str, str | bytes | None] | None)
HttpCookies: TypeAlias = (CookieJar | MutableMapping[str, str] | None)
HttpFilesItem: TypeAlias = (SupportsRead[str | bytes] | str | bytes | tuple[
    str | None, SupportsRead[str | bytes] | str | bytes] | tuple[
                                str | None, SupportsRead[str | bytes] | str | bytes, str] | tuple[
                                str | None, SupportsRead[str | bytes] | str | bytes, str, Mapping[str, str]])
HttpFiles: TypeAlias = (Mapping[str, HttpFilesItem] |
                        Iterable[tuple[str, HttpFilesItem]] | None)
HttpAuth: TypeAlias = (tuple[str, str] | AuthBase | Callable[[PreparedRequest], PreparedRequest] | None)
HttpTimeout: TypeAlias = (float | tuple[float, float] | tuple[float, None] | None)
HttpHooks: TypeAlias = (Mapping[str, Iterable[Callable[[Response], Any]] | Callable[[Response], Any]] | None)
HttpCert: TypeAlias = (str | tuple[str, str] | None)


def _sanitize_for_json(obj: Any) -> Any:
    """Recursively replace NaN/Infinity values with None."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [_sanitize_for_json(v) for v in obj]
    return obj


def _safe_json_dumps(data: Any) -> str:
    """Safely serialize data to JSON, replacing invalid numbers."""
    sanitized = _sanitize_for_json(data)
    return json.dumps(sanitized, allow_nan=False)


def http_request(method: HttpMethod, **kwargs):
    if "timeout" not in kwargs or kwargs["timeout"] is None:
        kwargs["timeout"] = (10, 1200)
    response = requests.request(method=method.name, **kwargs)
    if not response.ok:
        print("HTTP error response:", response.status_code, response.text)
    response.raise_for_status()
    return response


def http_get(url: str | bytes, params: HttpSupportsItems = None, headers: HttpHeaders = None, auth: HttpAuth = None):
    response = http_request(HttpMethod.GET, url=url, params=params, headers=headers, auth=auth)
    return response.json()


def http_post(url: str | bytes, params: HttpSupportsItems = None, headers: HttpHeaders = None, auth: HttpAuth = None,
              data: HttpData = None, files: HttpFiles = None, ):
    if data is not None and headers.get('Content-Type') == 'application/json':
        data = _safe_json_dumps(data)
    response = http_request(HttpMethod.POST, url=url, params=params, headers=headers, auth=auth, data=data, files=files)
    return response.json()


def http_get_raw(url: str | bytes, params: HttpSupportsItems = None, headers: HttpHeaders = None,
                 auth: HttpAuth = None):
    response = http_request(HttpMethod.GET, url=url, params=params, headers=headers, auth=auth, stream=True)
    return response.raw
