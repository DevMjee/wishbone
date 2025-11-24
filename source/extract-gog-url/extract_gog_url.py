"""Script that web scrapes url and extracts price from GOG"""

import re
from bs4 import BeautifulSoup
import requests

URL = "https://www.gog.com/en/game/captain_blood"


def fetch_page_html(url: str) -> str:
    """Request the page and return the HTML page"""
    response = requests.get(url, timeout=600)
    response.raise_for_status()
    return response.text


def extract_script_block(html: str) -> str:
    """Extract the <script> tag in <body> that contains price info"""
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.body.script

    if not script_tag or not script_tag.string:
        raise ValueError("Unable to find script data in page")

    return script_tag.string


def extract_amount(script_text: str, keyword: str) -> str:
    """Given script text and keyword ('finalAmount' or 'baseAmount'), extract price using regex"""
    pattern = rf'{keyword}":"([\d.]+)"'
    match = re.search(pattern, script_text)
    if not match:
        raise ValueError(f"Keyword '{keyword}' not found")

    return float(match.group(1))


def main():
    html = fetch_page_html(URL)
    script_text = extract_script_block(html)

    final_amount = extract_amount(script_text, "finalAmount")
    base_amount = extract_amount(script_text, "baseAmount")

    print(f"Final Amount: {final_amount}")
    print(f"Base Amount: {base_amount}")


if __name__ == "__main__":
    main()
