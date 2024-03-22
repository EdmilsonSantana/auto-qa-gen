import fitz
import os
import re

def extract_text(page):
    text = page.get_text()
    text = re.sub(r'OMECANICO.COM.BR .*', '', text)
    text = re.sub(r'\d+\n', '', text)
    text = re.sub(r"-\s+", '', text)
    text = re.sub(r'\n', ' ', text)
    return text

def extract_summary_sections(summary_page):
    text = summary_page.get_text()
    sections = re.findall(r'\d{2,4} [A-Z]+.*', text)

    if (len(sections) == 0):
        raise Exception('Summary sections not found')

    summary_sections = {}
    for section in sections:
        [page, title] = section.split(maxsplit=1)
        summary_sections[title] = page
    return summary_sections

def find_summary_page(doc):
    for i, page in enumerate(doc):
        if "SUMÁRIO" in page.get_text():
            return i, page
    raise Exception('Page summary not found')


def find_page_index_by_title(doc, summary_sections, summary_title):
    page_number = summary_sections[summary_title]
    for i, page in enumerate(doc):
        if re.search(f'^{page_number}\\n', page.get_text()):
            return i
    raise Exception(f'Page "{summary_title}" not found')


def extract_pdf_contents(filename):
    dest_file = f"{base_dir}/data.txt"

    if os.path.exists(dest_file):
        print(f"Removing existing {dest_file}")
        os.remove(dest_file)
   
    try:
        pdf_content = []
        doc = fitz.open(f"{base_dir}/{filename}")

        print(f'Processing {filename} with {len(doc)} pages')

        [summary_page_index, summary_page] = find_summary_page(doc)
        summary_sections = extract_summary_sections(summary_page)
        business_panel_page_index = find_page_index_by_title(doc, summary_sections, 'PAINEL DE NEGÓCIOS')

        for i, page in enumerate(doc):
            if (i > summary_page_index and i < business_panel_page_index):
                text = extract_text(page)
                pdf_content.append(text)

        f_write = open(dest_file, "a")
        f_read = open(dest_file, "r")

        pdf_text_content = "".join(pdf_content)

        print(f"Corpus with {len(f_read.read())} length")
        print(f"Writing content with {len(pdf_text_content)} length")

        f_write.write(pdf_text_content)
        f_write.close()        
    except Exception as error:
        print(f"Failed to extract {filename}", error)


if __name__ == "__main__":
    base_dir = './data'
    pdf_filenames = os.listdir(base_dir)
    pdf_filenames.sort()
    for filename in [pdf_filenames[-3]]:
        extract_pdf_contents(filename)

   
