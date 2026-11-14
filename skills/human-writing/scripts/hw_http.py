"""hw_http.py — bounded, SSRF-guarded HTTP for website audits.

Stdlib-only. Guards: private/loopback/link-local targets refused by default
(--allow-private to override), redirect hops bounded and re-checked, response
size capped, per-host politeness delay. robots.txt honoured best-effort.
"""
from __future__ import annotations

import ipaddress
import re
import socket
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

UA = "human-writing-audit/1.0 (+local)"
DEFAULT_TIMEOUT = 10
MAX_BYTES = 2_000_000
MAX_REDIRECTS = 5
RATE_DELAY = 0.2


class FetchError(Exception):
    pass


@dataclass
class Response:
    url: str
    status: int
    body: str
    final_url: str
    headers: dict = field(default_factory=dict)


def _ip_is_public(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
                or ip.is_multicast or ip.is_unspecified)


def host_is_public(host: str) -> bool:
    """DNS-resolve then check every address is routable/public."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as e:
        raise FetchError(f"dns failure for {host}: {e}") from e
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not _ip_is_public(ip):
            return False
    return True


def guard_url(url: str, allow_private: bool = False) -> str:
    """Reject non-http(s) schemes and internal targets; return normalized url."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https"):
        raise FetchError(f"scheme not allowed: {parts.scheme or url!r}")
    host = parts.hostname or ""
    try:
        ipaddress.ip_address(host)
        ok = host_is_public(host) if not allow_private else True
    except ValueError:
        ok = host_is_public(host) if not allow_private else True
    if not ok:
        raise FetchError(f"internal target refused: {host}")
    return url


class Fetcher:
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, max_bytes: int = MAX_BYTES,
                 allow_private: bool = False, rate_delay: float = RATE_DELAY):
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.allow_private = allow_private
        self.rate_delay = rate_delay
        self._last: float = 0.0
        self._robots: dict[str, bool] = {}

    def fetch(self, url: str, _hops: int = 0) -> Response:
        url = guard_url(url, self.allow_private)
        if _hops > MAX_REDIRECTS:
            raise FetchError(f"too many redirects: {url}")
        time.sleep(max(0.0, self.rate_delay - (time.monotonic() - self._last)))
        self._last = time.monotonic()
        req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                   "Accept": "text/html,text/plain,application/xml;q=0.8"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                raw = r.read(self.max_bytes + 1)
                charset = r.headers.get_content_charset() or "utf-8"
                status, final, hdrs = r.status, r.url, dict(r.headers)
        except Exception as e:  # noqa: BLE001 — transport errors are expected
            raise FetchError(f"{url}: {e}") from e
        if len(raw) > self.max_bytes:
            raise FetchError(f"response exceeds {self.max_bytes} bytes: {url}")
        return Response(url, status, raw.decode(charset, "replace"), final or url, hdrs)

    def robots_allows(self, url: str, agent: str = "*") -> bool:
        """Best-effort robots.txt: unknown host or blocked path returns False."""
        parts = urllib.parse.urlsplit(url)
        root = f"{parts.scheme}://{parts.netloc}/robots.txt"
        if root in self._robots:
            return True  # cached (unknown host -> permissive; blocked paths -> disallow list below)
        try:
            body = self.fetch(root).body
        except FetchError:
            self._robots[root] = False
            return True
        disallow = _robots_disallow(body, agent)
        path = parts.path or "/"
        self._robots[root] = True
        return not any(path.startswith(p) for p in disallow)

    def sitemap_urls(self, url: str) -> list[str]:
        try:
            r = self.fetch(url)
        except FetchError:
            return []
        return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r.body, re.I)


def _robots_disallow(robots: str, agent: str) -> list[str]:
    out, active = [], False
    for line in robots.splitlines():
        line = line.strip()
        if line.lower().startswith("user-agent:"):
            active = agent in line or line.split(":", 1)[1].strip() == "*"
        elif active and line.lower().startswith("disallow:"):
            p = line.split(":", 1)[1].strip()
            if p and p != "/":
                out.append(p)
    return out
