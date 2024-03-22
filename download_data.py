from selenium import webdriver
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import json
import os
import re

options = webdriver.ChromeOptions()
options.add_argument('headless')
browser = webdriver.Chrome(options=options)
browser.get('https://omecanico.com.br/edicoes-revista-mecanico/')

page = BeautifulSoup(browser.page_source, features='html.parser')

scriptTag = page.select_one('div#fb-root ~ script ~ script')
pdfStrArray = scriptTag.text.replace('<script type="text/javascript">', '') \
    .replace('</script>', '') \
    .replace('var et_link_options_data = ', '') \
    .replace(';', '') \
    .strip()
pdfLinks = json.loads(pdfStrArray)

print(f"Found {len(pdfLinks)} PDFs to download.")

for link in pdfLinks:
    url = urlparse(link['url'])
    filename = re.findall(r'\d{3}', os.path.basename(url.path))[0]
    file = Path(f"./data/{filename}.pdf")
    print(f"Downloading {filename}...")
    response = requests.get(link['url'])
    file.write_bytes(response.content)

browser.quit()