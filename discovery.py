import os
import requests
from urllib.parse import urlparse

def build_queries(keyword, wilaya="All Algeria", language="French"):
    location = "" if wilaya == "All Algeria" else f" {wilaya}"
    phrases = []
    if language in ("French", "French + Arabic"):
        phrases += [
            f"fournisseur {keyword}{location} Algérie",
            f"distributeur {keyword}{location} Algérie",
            f"grossiste {keyword}{location} Algérie",
        ]
    if language in ("Arabic", "French + Arabic"):
        phrases += [
            f"مورد {keyword}{location} الجزائر",
            f"موزع {keyword}{location} الجزائر",
        ]
    return phrases

def run_search(query, max_results=10, demo_if_unconfigured=True):
    """
    Uses Brave Search API when BRAVE_SEARCH_API_KEY is configured.
    Never scrapes Google result pages directly.
    """
    api_key = os.getenv("BRAVE_SEARCH_API_KEY", "").strip()
    if not api_key:
        try:
            import streamlit as st
            api_key = str(st.secrets.get("BRAVE_SEARCH_API_KEY", "")).strip()
        except Exception:
            api_key = ""
    if api_key:
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"Accept": "application/json", "X-Subscription-Token": api_key},
            params={"q": query, "count": min(max_results, 20), "country": "DZ", "search_lang": "fr"},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        rows = []
        for item in payload.get("web", {}).get("results", []):
            url = item.get("url", "")
            host = urlparse(url).netloc
            rows.append({
                "company_name": item.get("title", ""),
                "activity": query,
                "wilaya": "",
                "phone": "",
                "email": "",
                "website": f"{urlparse(url).scheme}://{host}" if host else "",
                "social_url": "",
                "source_url": url,
                "source_name": "Brave Search API",
                "evidence": item.get("description", ""),
                "verification_status": "Unverified",
                "notes": "Search-result lead; verify company identity and supplier status."
            })
        return rows

    if demo_if_unconfigured:
        return [{
            "company_name": "DEMO — configure BRAVE_SEARCH_API_KEY",
            "activity": query,
            "wilaya": "",
            "phone": "",
            "email": "",
            "website": "",
            "social_url": "",
            "source_url": f"demo://{query.replace(' ', '-')}",
            "source_name": "Demo mode",
            "evidence": "This is a placeholder, not a real supplier result.",
            "verification_status": "Unverified",
            "notes": "Add an API key in .env to perform real searches."
        }]
    return []
