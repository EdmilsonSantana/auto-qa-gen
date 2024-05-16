from models import IModel
from . import PromptRequest, PromptTemplate, PromptHandler, PromptValidationHandler
import uuid


class QuestionAnswerExtractionPrompt(PromptHandler):
    def __init__(self, model: IModel, number_of_questions: int = 5) -> None:
        super().__init__(model)
        self.number_of_questions = number_of_questions

    def get_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            name="questions",
            system_prompt=f"""
            You are a specialist in vehicle repair and maintenance and your goal is to extract {self.number_of_questions} questions and answers related to a certain topic from a document.
            Here are some conditions that you have to follow to achieve your goal:

            - You should add details to the question and answer so that you can understand it without knowing the context.
            - You should not create questions for contents not related to vehicle repair and maintenance.
            - The answers should only contain the content originating from the document.
            - The question should not include text that already answers the question.
            - The language used to generate questions and answers should always be Brazilian Portuguese.
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

            - You should not create duplicate questions.
            - The language used in the response should always be Brazilian Portuguese.
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
            Given a document and a question, classify the relevance of the question in relation to the document with a score between 0 and 1.0 and a reason for the score, considering 1.0 as a very related question and 0 as an unrelated question. Your output should be a JSON for an object representing the score and the reason. It should have the fields "score" and "reason" where "score" is a float and "reason" is a string.

            examples:

            Question: Posso apertar a porca do rolamento ?
            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, não se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: {"score": 0.8, "reason": "A pergunta aborda diretamente um tópico mencionado no documento, especificamente sobre apertar a porca do rolamento, indicando relevância. No entanto, não se alinha totalmente com o contexto, pois o documento principalmente alerta contra o aperto excessivo e discute possíveis problemas relacionados à lubrificação e diferentes composições químicas de graxa."}
            Question: Devo substituir a graxa de rolamentos dianteiros selados ?
            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, não se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: {"score": 1.0, "reason": "A pergunta está diretamente relacionada ao conteúdo do documento, pois aborda a substituição da graxa em rolamentos dianteiros selados, o que é explicitamente mencionado no texto. Portanto, é altamente relevante e recebe uma pontuação máxima de 1.0."}
            Question: Como funciona um motor a combustão ?
            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, não se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: {"score": 0.0, "reason": "A pergunta não está relacionada ao conteúdo do documento. O documento trata sobre a importância de não apertar excessivamente a porca do rolamento e os problemas associados à substituição da graxa em rolamentos dianteiros selados. Não aborda o funcionamento de um motor a combustão, portanto, a pergunta é considerada irrelevante para este documento, recebendo uma pontuação de 0.0."}""",
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
            Given a document, a question and an answer, using knowledge of the document classify whether the question is being answered correctly. The classification will be with a score between 0 and 1.0 and a justification for this score, considering 1.0 as a completely correct answer and 0 as a completely wrong answer. Your output should be a JSON to an object representing the score and reason. It should have the fields “score” and “reason” where “score” is a float and “reason” is a string.

            examples:

            Question: Posso apertar a porca do rolamento ?
            Answer: O aperto excessivo da porca afeta diretamente a vida útil do rolamento.
            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, não se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Response: {"score": 1.0, "reason": "A resposta aborda diretamente a questão, afirmando que o aperto excessivo da porca afeta a vida útil do rolamento, o que está alinhado perfeitamente com a preocupação de apertar a porca do rolamento."}
            Question: Devo substituir a graxa de rolamentos dianteiros selados ?
            Answer: Em rolamentos dianteiros selados, nunca substitua a graxa ou complete os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, não se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Response: {"score": 0.8, "reason": "Embora a resposta forneça uma recomendação clara de não substituir a graxa em rolamentos dianteiros selados, ela não responde diretamente à pergunta sobre se deve substituir a graxa. No entanto, a informação fornecida é relevante para a manutenção dos rolamentos dianteiros selados, o que contribui para uma pontuação alta."}
            Question: Como funciona um motor a combustão ?
            Answer: Os motores de combustão interna são máquinas térmicas que transformam a energia proveniente de uma reação química em energia mecânica.
            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, não se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Response: {"score": 0.0, "reason": "A resposta não está relacionada ao funcionamento de um motor a combustão. Ela menciona a afetação da vida útil de um rolamento devido ao aperto excessivo da porca, o que não tem relevância para a pergunta sobre motores a combustão."}
            Question: Devo substituir a graxa de rolamentos dianteiros selados ?
            Answer: Em rolamentos dianteiros selados, substitua a graxa e complete os espaços internos, porque não existe risco de uma reação entre as graxas com composições químicas diferentes.
            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, não se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Response: {"score": 0.0, "reason": "A resposta contradiz diretamente o conteúdo do documento, que recomenda não substituir a graxa em rolamentos dianteiros selados devido ao risco de reação entre diferentes composições químicas. Portanto, a resposta é considerada incorreta."}
            """,
            user_prompt="""
            Question: {question}
            Answer: {answer}
            Document: {document}
            Response:""",
            variables=['question', 'answer', 'document']
        )
