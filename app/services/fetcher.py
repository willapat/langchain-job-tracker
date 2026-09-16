import ipaddress
import json
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

MAX_BYTES = 2 * 1024 * 1024
MAX_REDIRECTS = 3
TIMEOUT = httpx.Timeout(8.0)
MIN_READABLE_CHARS = 200


class FetchError(Exception):
    def __init__(self, code: str, message: str, fallback: str | None = "paste_description"):
        self.code = code
        self.message = message
        self.fallback = fallback
        super().__init__(message)


def _is_blocked_ip(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def _assert_host_is_public(host: str) -> None:
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise FetchError("URL_FETCH_FAILED", f"Could not resolve host: {host}") from exc

    for info in infos:
        ip = info[4][0]
        if _is_blocked_ip(ip):
            raise FetchError("URL_BLOCKED", "This URL resolves to a private or internal address.", fallback=None)


def _assert_url_allowed(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise FetchError("URL_BLOCKED", "Only http(s) URLs are allowed.", fallback=None)
    if not parsed.hostname:
        raise FetchError("URL_BLOCKED", "URL has no host.", fallback=None)
    _assert_host_is_public(parsed.hostname)


@dataclass
class FetchedPage:
    text: str
    final_url: str


def fetch_url(url: str) -> FetchedPage:
    """Fetch a user-supplied URL with SSRF guards, following a bounded number of
    redirects and re-validating the target of each hop."""
    current_url = url
    with httpx.Client(follow_redirects=False, timeout=TIMEOUT) as client:
        for _ in range(MAX_REDIRECTS + 1):
            _assert_url_allowed(current_url)
            try:
                with client.stream("GET", current_url, headers={"User-Agent": "Waypoint-JobTracker/1.0"}) as resp:
                    if resp.is_redirect:
                        location = resp.headers.get("location")
                        if not location:
                            raise FetchError("URL_FETCH_FAILED", "Redirect with no Location header.")
                        current_url = httpx.URL(current_url).join(location).human_repr()
                        continue

                    content_type = resp.headers.get("content-type", "")
                    if "text/html" not in content_type and "application/xhtml" not in content_type:
                        raise FetchError(
                            "URL_NOT_READABLE", f"Unsupported content type: {content_type or 'unknown'}"
                        )

                    chunks = bytearray()
                    for chunk in resp.iter_bytes():
                        chunks.extend(chunk)
                        if len(chunks) > MAX_BYTES:
                            raise FetchError("URL_FETCH_FAILED", "Page exceeded the size limit.")

                    if resp.status_code >= 400:
                        raise FetchError("URL_FETCH_FAILED", f"Server returned HTTP {resp.status_code}.")

                    return FetchedPage(text=bytes(chunks).decode("utf-8", errors="replace"), final_url=current_url)
            except httpx.RequestError as exc:
                raise FetchError("URL_FETCH_FAILED", f"Request failed: {exc}") from exc

        raise FetchError("URL_FETCH_FAILED", "Too many redirects.")


def extract_readable_text(html: str) -> str:
    """Prefer JSON-LD JobPosting structured data (Greenhouse/Lever/Ashby emit this),
    fall back to stripped visible text."""
    soup = BeautifulSoup(html, "html.parser")

    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        candidates = data if isinstance(data, list) else [data]
        for candidate in candidates:
            if isinstance(candidate, dict) and candidate.get("@type") == "JobPosting":
                parts = [
                    candidate.get("title", ""),
                    candidate.get("hiringOrganization", {}).get("name", "")
                    if isinstance(candidate.get("hiringOrganization"), dict)
                    else "",
                    BeautifulSoup(candidate.get("description", ""), "html.parser").get_text(" ", strip=True),
                ]
                text = "\n".join(p for p in parts if p)
                if text:
                    return text

    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
        tag.decompose()
    return soup.get_text(" ", strip=True)


def fetch_job_posting_text(url: str) -> str:
    page = fetch_url(url)
    text = extract_readable_text(page.text)
    if len(text) < MIN_READABLE_CHARS:
        raise FetchError(
            "URL_NOT_READABLE",
            "Couldn't find enough readable text on that page (it may require a login or JavaScript).",
        )
    return text
