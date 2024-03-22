from bs4 import BeautifulSoup
from selenium import webdriver
import json
import re
import os

sitemap_url = 'https://www.autozone.com/diy/category-sitemap'

def extract_fa_questions(page_content):
   faq_section = page_content.select('div.schema-faq-section')

   faq_questions = []
   for faq in faq_section:
      question = faq.select_one('strong').text
      answer = faq.select_one('.schema-faq-answer').text
      faq_questions.append(dict(question=question, answer=answer))

   return faq_questions
 
def remove_section(page_content, css_selector):
   section = page_content.select_one(css_selector)
   if section:
      section.decompose()

def extract_sitemap(data_dir):
    sitemap_filepath = f'{data_dir}/sitemap.json'

    if (os.path.exists(sitemap_filepath)):
      return json.load(open(sitemap_filepath))

    driver = webdriver.Safari()
    driver.get(sitemap_url)

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

    with open(sitemap_filepath, 'a') as fp:
        json.dump(sitemap, fp) 
    return sitemap

def extract_articles(data_dir):
   articles_filepath = f'{data_dir}/articles.json'

   if (os.path.exists(articles_filepath)):
      return json.load(open(articles_filepath))

   sitemap = extract_sitemap(data_dir)
   driver = webdriver.Safari()
   articles = []

   for category in sitemap:
      for article in category['articles']:
         try:
            href = article['href']
            print(f"Processing {href}")

            driver.get(href)

            article_page = BeautifulSoup(driver.page_source, 'html.parser')

            page_content = article_page.select_one('#az-blog-content')

            fa_questions = extract_fa_questions(page_content)

            # Removing unwanted sections
            remove_section(page_content, '.az-blog-post-section')
            remove_section(page_content, '.az-blog-content__products')
            remove_section(page_content, '.schema-faq')
            remove_section(page_content, '#faq-people-also-ask')

            # Removing Autozone ADs
            autozone_ads = page_content.find(lambda tag: tag.name == "p" and "autozone" in tag.text.lower())
            if (autozone_ads):
               autozone_ads.decompose()

            text_content = re.sub(r'\n\s*\n', '\n\n', page_content.text.strip())
            articles.append(dict(title=article['title'], content=text_content, category=category['title']))
         except Exception as error:
            print(f'Failed to extract {href}', error)

   with open(articles_filepath, 'a') as fp:
      json.dump(articles, fp) 

   driver.close()
