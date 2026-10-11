import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from datetime import datetime, timezone

USER_AGENT = "AlgeriaSupplierDiscovery/0.1 (+contact: configure-your-contact@example.com)"
_last_request_at = 0.0
MIN_SECONDS_BETWEEN_REQUESTS = 2.0

def _polite_get(url, timeout=15):
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    if elapsed < MIN_SECONDS_BETWEEN_REQUESTS:
        time.sleep(MIN_SECONDS_BETWEEN_REQUESTS - elapsed)
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout, allow_redirects=True)
    _last_request_at = time.monotonic()
    response.raise_for_status()
    return response

def allowed_by_robots(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        response = requests.get(robots_url, headers={"User-Agent": USER_AGENT}, timeout=8)
        if response.status_code == 404:
            return True
        if response.status_code >= 400:
            # Fail closed when robots policy cannot be checked.
            return False
        parser = RobotFileParser()
        parser.parse(response.text.splitlines())
        return parser.can_fetch(USER_AGENT, url)
    except requests.RequestException:
        return False

def enrich_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("URL must start with http:// or https://")
    if not allowed_by_robots(url):
        return {
            "company_name": "", "source_url": url, "source_name": parsed.netloc,
            "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "verification_status": "Unverified",
            "notes": "Skipped because robots.txt disallows access or could not be checked."
        }

    response = _polite_get(url)
    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type.lower():
        raise ValueError("Only HTML pages are supported in this first version.")
    soup = BeautifulSoup(response.text[:2_000_000], "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    description = ""
    meta = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    if meta:
        description = meta.get("content", "").strip()
    text = soup.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)[:1200]

    emails = sorted(set(re.findall(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", response.text, re.I)))
    # Avoid guessing a phone number from arbitrary page text; users can review and add it manually.
    canonical = soup.find("link", rel="canonical")
    source_url = urljoin(url, canonical.get("href")) if canonical and canonical.get("href") else url

    return {
        "company_name": title,
        "activity": description,
        "wilaya": "",
        "phone": "",
        "email": "; ".join(emails[:5]),
        "website": f"{parsed.scheme}://{parsed.netloc}",
        "social_url": "",
        "source_url": source_url,
        "source_name": parsed.netloc,
        "evidence": text,
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "verification_status": "Unverified",
        "notes": "Extracted from a permitted public HTML page; confirm company name and contact details."
    }
