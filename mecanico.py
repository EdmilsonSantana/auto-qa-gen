import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import os
import re

def get_data(category, page):
    print(f"Processing page {page} from category {category}")

    url = f'https://omecanico.com.br/wp-json/wp/v2/posts?categories={category}&page={page}'

    try:
        req = urlopen(Request(
            url=url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        ))
    except HTTPError as e:
        if e.code != 200:
            print(f"HTTP Error {e}")
            return None

    posts = {}

    content = req.read().decode(req.headers.get_content_charset())
    res = json.loads(content)
        
    for item in res:
        page = BeautifulSoup(item['content']['rendered'], 'html.parser')
        sentences = []
        for paragraph in page.find_all('p'):
            text = paragraph.get_text()
            text = text \
                .replace('Posts Relacionados', '') \
                .replace("\u00a0", ' ') \
                .replace("\n", " ") \
                .strip()
            text = re.sub(r'\n\s*\n', '\n\n', text)
            if len(text) > 0:
                sentences.append(text)

        posts[item['id']] = dict(
            id=item['id'],
            title=item['title']['rendered'],
            sentences=sentences,
            category=category
        )

    print(f"Found {len(posts)} posts")

    return posts

categories = [
    4854, # Undercar
    4670, # Transmissão
    4673, # Suspensão
    4855, # Raio X
    4668, # Motor
    10687, # Mecânica Diesel
    4672, # Injeção  de Ignição 
    4851, # Híbridos e elétricos
    4850, # Freios
    4669, # Direção
    4674, # Climatização
    4849, # Carga e Partida 
    4848 # Arrefecimento
]

def extract_posts():
    mecanico_filepath = './data/mecanico.json'

    if (os.path.exists(mecanico_filepath)):
        return json.load(open(mecanico_filepath))

    all_posts = {}
    for category in categories:
        page = 1

        while True:
            posts = get_data(category, page)
            if posts is None:
                break
            all_posts.update(posts)
            print(f"Total posts {len(all_posts)}")
            page += 1
            
    with open('./data/mecanico.json', 'w', encoding='utf-8') as fp:
        json.dump(list(all_posts.values()), fp, ensure_ascii=False)

    return all_posts
