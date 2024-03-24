from bs4 import BeautifulSoup
from selenium import webdriver
import json
import re
import os

sitemap_url = 'https://www.autozone.com/diy/category-sitemap'


def extract_faq_questions(page_content):
    faq_section = page_content.select('div.schema-faq-section')

    faq_questions = []
    for faq in faq_section:
        question = replace_unicode_chars(faq.select_one('strong').text)
        answer = replace_unicode_chars(faq.select_one('.schema-faq-answer').text)
        faq_questions.append(dict(question=question, answer=answer))

    return faq_questions


def remove_section(page_content, css_selector):
    section = page_content.select_one(css_selector)
    if section:
        section.decompose()

def replace_unicode_chars(text):
    return re.sub(u"(\u2018|\u2019|\u202f)", "'", re.sub(u"\u202f", " ", text))

def extract_sitemap(data_dir):
    sitemap_filepath = f'{data_dir}/sitemap.json'

    if (os.path.exists(sitemap_filepath)):
        return json.load(open(sitemap_filepath))

    driver = webdriver.Chrome()
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
            item['articles'].append(
                dict(href=href, title=title, description=description))

    with open(sitemap_filepath, 'a') as fp:
        json.dump(sitemap, fp)
    return sitemap

def remove_paragraphs(page_content, text):
    element = page_content.find(
        lambda tag: tag.name == "p" and text in tag.text.lower())
    if (element):
        element.decompose()

def parse_page_content(page_content):
    # Removing unwanted sections
    remove_section(page_content, '.az-blog-post-section')
    remove_section(page_content, '.az-blog-content__products')
    remove_section(page_content, '.schema-faq')
    remove_section(page_content, '#faq-people-also-ask')
    remove_section(page_content, '#h-faq-people-also-ask')
    remove_section(page_content, '#h-helpful-resources')

    # Removing Autozone ADs
    remove_paragraphs(page_content, text="autozone")

    text_content = replace_unicode_chars(page_content.text.strip())
    text_content = re.sub(r'\n\s*\n', '\n\n', text_content)

    sentences = text_content.split('.')
    for sentence in sentences:
        if "preferred shops" in sentence.lower():
            text_content = text_content.replace(f"{sentence}.", "")

    return text_content


def extract_articles(data_dir):
    articles_filepath = f'{data_dir}/articles.json'

    if (os.path.exists(articles_filepath)):
        return json.load(open(articles_filepath))

    sitemap = extract_sitemap(data_dir)
    driver = webdriver.Chrome()
    articles = []

    for category in sitemap:
        for article in category['articles']:
            try:
                href = article['href']
                print(f"Processing {href}")

                driver.get(href)

                article_page = BeautifulSoup(driver.page_source, 'html.parser')
                page_content = article_page.select_one('#az-blog-content')

                faq_questions = extract_faq_questions(page_content)

                articles.append(dict(
                    title=article['title'],
                    content=parse_page_content(page_content),
                    category=category['title'],
                    faq_questions=faq_questions))
            except Exception as error:
                print(f'Failed to extract {href}', error)

    with open(articles_filepath, 'w') as fp:
        json.dump(articles, fp)

    driver.close()


if __name__ == "__main__":
    data_dir = './data'
    articles_filepath = f"{data_dir}/articles.json"
    if (os.path.exists(articles_filepath)):
      os.remove(articles_filepath)

    extract_articles(data_dir)
