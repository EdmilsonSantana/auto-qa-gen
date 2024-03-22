from bs4 import BeautifulSoup
from selenium import webdriver
import json

driver = webdriver.Safari()

driver.get("https://www.autozone.com/diy/category-sitemap")

category_sitemap_page = BeautifulSoup(driver.page_source, features='lxml')

category_links = category_sitemap_page.select('.az-category-pod')

sitemap = []

for link in category_links:
    href = link['href']
    title = link.select_one('.az-category-pod__title').text
    sitemap.append(dict(href=href, title=title, articles=[]))

for item in sitemap:
    driver.get(item['href'])

    category_page = BeautifulSoup(driver.page_source, features='lxml')

    article_links = category_page.select('a.az-blog-pod')

    for link in article_links:
        href = link['href']
        title = link.select_one('.az-blog-pod__title').text
        description = link.select_one('.az-blog-pod__description').text
        item['articles'].append(dict(href=href, title=title, description=description))

with open('./data/sitemap.json', 'a') as fp:
    json.dump(sitemap, fp) 


driver.close()