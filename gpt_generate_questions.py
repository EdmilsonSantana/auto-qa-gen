from dotenv import load_dotenv
from pypdf import PdfReader
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from operator import itemgetter
from langchain.schema.output_parser import StrOutputParser
import re
# langchain langchain-openai pypdf python-dotenv pypdf

load_dotenv()

pdf = PdfReader('./data/356.pdf')

def extract_text(page):
    text = page.extract_text(extraction_mode="layout")
    text = re.sub(r'OMECANICO.COM.BR .*', '', text)
    text = re.sub(r'\d+\n', '', text)
    text = re.sub(r"-\s+", '', text)
    text = re.sub(r'\n', ' ', text)
    return text

page_number = 2
page = extract_text(pdf.pages[page_number])

#document = open('./data/data.txt').read()

llm = ChatOpenAI(verbose=True)

template = """
You are a pdf document reader specialized in read magazines with vehicle repair and maintenance content
and capable of extract questions regarding the content.

You should not create questions for contents not realted to vehicle repair and maintenance.

You have to output the questions with their respective answers and the answers should only contain the exact
same text originating from the document content.

You have to create as many questions as necessary to answer the entire content of the document.
There cannot be any content in the given document without a question related to it.

If there aren't enough content to create questions, you should reply with 'None'.

Here is the document:
{input}
"""
prompt = ChatPromptTemplate.from_template(template)

chain = prompt | llm | StrOutputParser()

print(page)

#print(chain.invoke({"input": page}))

