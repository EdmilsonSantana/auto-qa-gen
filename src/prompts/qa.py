from models import IModel
from . import PromptRequest, PromptTemplate, PromptHandler, PromptValidationHandler
import uuid


class QuestionAnswerExtractionPrompt(PromptHandler):
    def __init__(self, model: IModel, subject: str, number_of_questions: int = 5) -> None:
        super().__init__(model)
        self.subject = subject
        self.number_of_questions = number_of_questions

    def get_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            name="questions",
            system_prompt=f"""
            You are a specialist in {self.subject} and your goal is to extract {self.number_of_questions} questions and answers related to a certain topic from a document.
            Here are some conditions that you have to follow to achieve your goal:

            - You should add details to the question and answer so that you can understand it without knowing the context.
            - You should not create questions for contents not related to {self.subject}.
            - The answers should only contain the content originating from the document.
            - The language used to generate questions and answers should always be same as the document.
            - Your response should always be only a well-formed JSON array with the questions and answers.

            examples:

            Topic: Rolamentos dianteiros
            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento.
            Em rolamentos dianteiros selados, nunca se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação
            entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.

            Answer:
            [
                {{
                    "question": "Posso apertar a porca do rolamento ?",
                    "answer": "O aperto excessivo da porca afeta diretamente a vida útil do rolamento."
                }},
                {{
                    "question": "Devo substituir a graxa de rolamentos dianteiros selados ?",
                    "answer": "Em rolamentos dianteiros selados, nunca substitua a graxa ou complete os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento."
                }}
            ]""",
            user_prompt="""
            Topic: {topic}
            Document: {document}
            Answer:""",
            variables=['topic', 'document']
        )

    def to_object(self, json: dict | list, request: PromptRequest) -> list[PromptRequest]:
        return [request.update(data=dict(question=qa['question'], answer=qa['answer']), metadata=dict())
                for qa in json]


class QuestionAnswerVariationsPrompt(PromptHandler):
    def __init__(self, model: IModel, number_of_questions: int = 5) -> None:
        super().__init__(model)
        self.number_of_questions = number_of_questions

    def get_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            name="question_answer_variations",
            system_prompt=f"""
            Given a document, a question, and its respective answer, your goal is to grammatically and semantically rephrase the question and answer to create {self.number_of_questions} variations. 
            Here are some conditions that you have to follow to achieve your goal:

            - The language used in response should always be the same as the document.
            - Your response should always be only a well-formed JSON array with the questions and answers.

            examples:

            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento.
            Em rolamentos dianteiros selados, nunca se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação
            entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Question: Posso apertar a porca do rolamento ?
            Answer: O aperto excessivo da porca afeta diretamente a vida útil do rolamento.
            Response:
            [
                {{
                    "question": "Existe a possibilidade de apertar a porca do rolamento?",
                    "answer": "O excesso de aperto da porca tem um impacto direto na durabilidade do rolamento."
                }},
                {{
                    "question": "Será que posso ajustar a porca do rolamento?",
                    "answer": "O aperto excessivo da porca influencia diretamente na vida útil do rolamento."
                }},
                {{
                    "question": "É viável apertar a porca do rolamento?",
                    "answer": "O aperto exagerado da porca tem um efeito direto na vida útil do rolamento."
                }},
                {{
                    "question": "É possível ajustar a porca do rolamento?",
                    "answer": "O aperto excessivo da porca afeta diretamente a durabilidade do rolamento."
                }},
                {{
                    "question": "Posso realizar o aperto da porca do rolamento?",
                    "answer": "O aperto excessivo da porca tem um impacto direto na vida útil do rolamento."
                }}
            ]""",
            user_prompt="""
            Document: {document}
            Question: {question}
            Answer: {answer}
            Response:""",
            variables=['document', 'question', 'answer']
        )

    def to_object(self, json: dict | list, request: PromptRequest) -> list[PromptRequest]:
        requests = [request.update(data=dict(question=qa['question'], answer=qa['answer']), metadata=dict())
                    for qa in json]
        requests.append(request)
        return requests


class QuestionsValidationPrompt(PromptValidationHandler):
    def get_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            name="questions_validation",
            system_prompt="""
            Given a document and a question, classify how related the question is to the document with a score between 0 and 1.0 and a reason for the score, considering 1.0 as a very related question and 0 as an unrelated question. Your output should be a JSON for an object representing the score and the reason. It should have the fields "score" and "reason" where "score" is a float and "reason" is a string.

            examples:

            Question: Posso apertar a porca do rolamento ?
            Document: O cuidado com o meio ambiente é uma preocupação global imprescindível para o desenvolvimento sustentável. No mundo dos automóveis, essa discussão é cada vez maior, com o aumento do rigor na legislação em diversos países - o que acelera a evolução de veículos de propulsão alternativa, como híbridos e elétricos. O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: {"score": 1.0, "reason": "A pergunta está relacionada ao tema do documento, que discute cuidados e manutenção relacionados aos rolamentos em automóveis. A pergunta se relaciona ao tema geral de cuidados e manutenção mecânica discutidos no documento."}
            Question: Devo substituir a graxa de rolamentos dianteiros selados ?
            Document: O cuidado com o meio ambiente é uma preocupação global imprescindível para o desenvolvimento sustentável. No mundo dos automóveis, essa discussão é cada vez maior, com o aumento do rigor na legislação em diversos países - o que acelera a evolução de veículos de propulsão alternativa, como híbridos e elétricos. O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: {"score": 1.0, "reason": "A pergunta está diretamente relacionada ao conteúdo do documento, que discute o cuidado e a manutenção de rolamentos dianteiros selados, incluindo o aviso contra a substituição ou adição de graxa devido a possíveis reações químicas e aumento de calor dentro do rolamento."}
            Question: Como funciona um motor a combustão ?
            Document: O cuidado com o meio ambiente é uma preocupação global imprescindível para o desenvolvimento sustentável. No mundo dos automóveis, essa discussão é cada vez maior, com o aumento do rigor na legislação em diversos países - o que acelera a evolução de veículos de propulsão alternativa, como híbridos e elétricos. O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: {"score": 0, "reason": "O documento discute preocupações ambientais e avanços em sistemas de propulsão alternativa para veículos, enquanto a pergunta é sobre o funcionamento de um motor a combustão, o que não está diretamente relacionado ao documento."}""",
            user_prompt="""
            Question: {question}
            Document: {document}
            Answer:""",
            variables=['question', 'document']
        )


class AnswerValidationPrompt(PromptValidationHandler):
    def get_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            name="answers_validation",
            system_prompt="""
            Given a document, a question, and an answer, classify whether the answer is correct using knowledge from the document. The classification will be with a score between 0 and 1.0 and a justification for this score, considering 1.0 as a completely correct answer and 0 as a completely wrong answer. Your output should be a JSON to an object representing the score and reason. It should have the fields “score” and “reason” where “score” is a float and “reason” is a string.

            examples:

            Question: Posso apertar a porca do rolamento ?
            Answer: O aperto excessivo da porca afeta diretamente a vida útil do rolamento.
            Document: O cuidado com o meio ambiente é uma preocupação global imprescindível para o desenvolvimento sustentável. No mundo dos automóveis, essa discussão é cada vez maior, com o aumento do rigor na legislação em diversos países - o que acelera a evolução de veículos de propulsão alternativa, como híbridos e elétricos. O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Response: {"score": 1.0, "reason": "A resposta está correta, confirmando que o aperto excessivo da porca afeta a vida útil do rolamento, o que é consistente com as informações fornecidas no documento."}
            Question: Devo substituir a graxa de rolamentos dianteiros selados ?
            Answer: "Em rolamentos dianteiros selados, nunca substitua a graxa ou complete os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Document: O cuidado com o meio ambiente é uma preocupação global imprescindível para o desenvolvimento sustentável. No mundo dos automóveis, essa discussão é cada vez maior, com o aumento do rigor na legislação em diversos países - o que acelera a evolução de veículos de propulsão alternativa, como híbridos e elétricos. O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Response: {"score": 1.0, "reason": "A resposta está correta, aconselhando contra a substituição da graxa em rolamentos dianteiros selados, citando possíveis problemas como reações químicas e aquecimento elevado dentro do rolamento, o que está alinhado com as informações fornecidas no documento."}
            Question: Como funciona um motor a combustão ?
            Answer: Os motores de combustão interna são máquinas térmicas que transformam a energia proveniente de uma reação química em energia mecânica.
            Document: O cuidado com o meio ambiente é uma preocupação global imprescindível para o desenvolvimento sustentável. No mundo dos automóveis, essa discussão é cada vez maior, com o aumento do rigor na legislação em diversos países - o que acelera a evolução de veículos de propulsão alternativa, como híbridos e elétricos. O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Response: {"score": 0.0, "reason": "A resposta não está correta, pois o documento não fornece informações relacionadas ao funcionamento de um motor a combustão."}
            Question: Devo substituir a graxa de rolamentos dianteiros selados ?
            Answer: "Em rolamentos dianteiros selados, substitua a graxa e complete os espaços internos, porque não existe risco de uma reação entre as graxas com composições químicas diferentes.
            Document: O cuidado com o meio ambiente é uma preocupação global imprescindível para o desenvolvimento sustentável. No mundo dos automóveis, essa discussão é cada vez maior, com o aumento do rigor na legislação em diversos países - o que acelera a evolução de veículos de propulsão alternativa, como híbridos e elétricos. O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Response: {"score": 0.0, "reason": "A resposta está incorreta. Recomendar a substituição da graxa em rolamentos dianteiros selados contradiz as instruções fornecidas no documento, que alertam explicitamente contra essa prática devido ao risco de reações químicas entre as graxas."}
            """,
            user_prompt="""
            Question: {question}
            Answer: {answer}
            Document: {document}
            Response:""",
            variables=['question', 'answer', 'document']
        )
