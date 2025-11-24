from bs4 import BeautifulSoup
import requests
import re
import pprint

URL = "https://www.gog.com/en/game/captain_blood"

response = requests.get(URL)
html_document = response.text

soup = BeautifulSoup(html_document, "html.parser")

print(soup.title.string.strip())

body_string = soup.body.script.string
find_final_amount_string = "finalAmount"
final_amount_index_found = body_string.find(find_final_amount_string)

r = final_amount_index_found
while body_string[r] != ",":
    r += 1

final_amount_string = body_string[final_amount_index_found:r]

find_base_amount_string = "baseAmount"
base_amount_index_found = body_string.find(find_base_amount_string)

r = base_amount_index_found
while body_string[r] != ",":
    r += 1

base_amount_string = body_string[base_amount_index_found:r]
# final_string = body_string[index_found:index_found+]

print(final_amount_string)
print(base_amount_string)
