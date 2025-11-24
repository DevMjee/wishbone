"""Script that web scrapes url and extracts price from GOG"""

import re
from bs4 import BeautifulSoup
import requests

URL = "https://www.gog.com/en/game/captain_blood"
KEYWORDS = ["finalAmount", "baseAmount"]


def fetch_page_html(url: str) -> str:
    """Request the page and return the HTML page"""
    response = requests.get(url, timeout=600)
    response.raise_for_status()
    return response.text


def find_price_script(soup) -> str:
    """Checks if a price script exists in the HTML page"""
    for script in soup.find_all("script"):
        if script.string and any(k in script.string for k in KEYWORDS):
            return script.string

    raise ValueError("No price script found in HTML")


def extract_amount(script_text: str, keyword: str) -> str:
    """Given script text and keyword ('finalAmount' or 'baseAmount'), extract price using regex"""
    pattern = rf'{keyword}":"([\d.]+)"'
    match = re.search(pattern, script_text)
    if not match:
        raise ValueError(f"Keyword '{keyword}' not found")

    return float(match.group(1))


def get_prices():
    html = fetch_page_html(URL)
    soup = BeautifulSoup(html, "html.parser")
    script_text = find_price_script(soup)

    final_amount = extract_amount(script_text, "finalAmount")
    base_amount = extract_amount(script_text, "baseAmount")

    return {
        "base_price": base_amount,
        "final_price": final_amount
    }


if __name__ == "__main__":
    print(get_prices())
