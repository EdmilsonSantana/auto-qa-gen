from bs4 import BeautifulSoup
from selenium import webdriver
import json
import re

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


if __name__ == "__main__":
   file = open('./data/sitemap.json')
   sitemap = json.load(file)
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

   with open('./data/articles.json', 'a') as fp:
      json.dump(articles, fp) 

   driver.close()

