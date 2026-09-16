import pytest

from app.services.fetcher import FetchError, _assert_url_allowed, extract_readable_text


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "http://localhost/",
        "http://169.254.169.254/latest/meta-data/",  # cloud metadata endpoint
        "http://10.0.0.5/",
        "http://192.168.1.1/",
        "ftp://example.com/",
        "file:///etc/passwd",
    ],
)
def test_blocked_urls_are_rejected(url):
    with pytest.raises(FetchError) as exc_info:
        _assert_url_allowed(url)
    assert exc_info.value.code == "URL_BLOCKED"
    assert exc_info.value.fallback is None


def test_public_url_is_allowed(monkeypatch):
    import app.services.fetcher as fetcher_module

    monkeypatch.setattr(
        fetcher_module.socket,
        "getaddrinfo",
        lambda host, port: [(2, 1, 6, "", ("93.184.216.34", 0))],
    )
    # should not raise for a public IP
    _assert_url_allowed("https://example.com/jobs/123")


def test_json_ld_job_posting_is_preferred():
    html = """
    <html><head>
    <script type="application/ld+json">
    {"@type": "JobPosting", "title": "Backend Engineer",
     "hiringOrganization": {"name": "Acme"},
     "description": "We need someone with 5+ years of Python experience and strong system design skills for this role."}
    </script>
    </head><body><nav>ignored nav text</nav><p>ignored body</p></body></html>
    """
    text = extract_readable_text(html)
    assert "Backend Engineer" in text
    assert "Acme" in text
    assert "ignored nav text" not in text


def test_falls_back_to_visible_text_without_json_ld():
    html = "<html><body><nav>skip</nav><p>" + ("Job description content. " * 20) + "</p></body></html>"
    text = extract_readable_text(html)
    assert "skip" not in text
    assert "Job description content." in text
