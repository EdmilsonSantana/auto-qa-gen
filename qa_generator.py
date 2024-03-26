from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from operator import itemgetter
from langchain.schema.output_parser import StrOutputParser
import json

load_dotenv()

mecanico_dataset = json.load(open('./data/mecanico.json', 'r'))

llm = ChatOpenAI(verbose=True)

template = """
You are a specialist in vehicle repair and maintenance and your goal is to 
extract questions and answers from articles that you read. Here are some criterias
that you have to follow to achieve your goal:

- You should not create questions for contents not related to vehicle repair and maintenance.
- You have to output the questions with their respective answers.
- The answers should only contain the exact same text originating from the article content.
- You have to create as many questions as necessary to answer the entire content of the article.
- There cannot be any content in the given document without a question related to it.
- If there aren't enough content to create questions, you should reply with 'None'.
- The language used to generate questions and answers should always be Brazilian Portuguese.
- Format the output as JSON with one key for the question and another for the answer.

Take guidance from the example below:

Input: {context}

Ouput: {questions}

Here is the article:
{input}
"""
prompt = ChatPromptTemplate.from_template(template)

chain = prompt | llm | StrOutputParser()

input = " ".join(mecanico_dataset[0]['sentences'])

context = """O aperto excessivo da porca afeta diretamente a vida útil do rolamento.
Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca
substituir a graxa ou completar os espaços internos, porque pode haver uma reação
entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento."""

questions = """
[
    {
        "question": "Posso apertar a porca do rolamento ?",
        "answer": "O aperto excessivo da porca afeta diretamente a vida útil do rolamento."
    },
    {
        "question": "Devo substituir a graxa de rolamentos dianteiros selados ? ",
        "answer": "Em rolamentos dianteiros selados, nunca substitua a graxa ou complete os espaços internos,
                porque pode haver uma reação entre as graxas com composições químicas diferentes, além de
                um aquecimento elevado no interior do rolamento."
    }
]
"""

print(chain.invoke({"input": input, "context": context, "questions": questions}))