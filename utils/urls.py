from __future__ import annotations

from urllib.parse import urlencode, urlsplit, urlunsplit


def append_query_parameters(url: str, **parameters: str) -> str:
    """Append encoded parameters without corrupting an existing query string."""

    parts = urlsplit(url)
    encoded = urlencode(parameters)
    query = f"{parts.query}&{encoded}" if parts.query else encoded
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))
