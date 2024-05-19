from models import IModel
from . import PromptRequest, PromptTemplate, PromptHandler, PromptValidationHandler


class TopicsExtractionPrompt(PromptHandler):
    def __init__(self, model: IModel, number_of_topics: int = 5) -> None:
        super().__init__(model)
        self._number_of_topics = number_of_topics

    def get_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            name="topics",
            system_prompt=f"""
            Given a document your goal is to extract {self._number_of_topics} topics that summarizes the content present in the document.
            Here are some criterias that you have to follow to achieve your goal:

            - You should extract the topics in Brazilian Portuguese.
            - You should not extract topics not related to vehicle repair and maintenance.
            - You should not extract single-word topics.
            - You should not extract topics based on images, figures, tables or graphic representations mentioned in the documents.
            - The output should be a JSON list of strings in the following format: ["topic", "topic", "topic"].
        
            examples:

            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, não se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: [\"Prevenção de reações químicas entre diferentes tipos de graxa\", \"Impacto do aperto excessivo da porca na vida útil do rolamento\", \"Cuidados específicos com a manutenção de rolamentos dianteiros selados\", \"Controle de aquecimento no interior do rolamento\", \"Manutenção de rolamentos dianteiros selados\"]
            Document: Entre os vários parâmetros levados em conta no projeto da suspensão de um carro, os três principais ângulos medidos no alinhamento de veículos leves são convergência e divergência (paralelismo horizontal entre as rodas), câmber (ângulo de inclinação lateral da roda em relação ao eixo vertical) e o cáster (inclinação do eixo vertical referente ao centro da circunferência da roda). Mas antes de instalar o equipamento de medição, o primeiro procedimento que o mecânico deve fazer é analisar os sintomas.
            Answer: [\"Parâmetros essenciais no projeto da suspensão de um carro\", \"Importância da análise dos sintomas antes da medição\", \"Convergência e divergência: impacto no alinhamento das rodas\", \"Câmber: influência do ângulo de inclinação lateral da roda\", \"Cáster: considerações sobre a inclinação do eixo vertical\"]""",
            user_prompt="""
            Document: {document}
            Answer:""",
            variables=['document']
        )

    def to_object(self, json: dict | list, request: PromptRequest) -> list[PromptRequest]:
        return [request.update(data=dict(topic=topic), metadata=dict()) for topic in json]


class TopicsValidationPrompt(PromptValidationHandler):
    def get_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            name="topics_validation",
            system_prompt="""
            Given a document and a topic, classify the relevance of the topic in relation to the document with a score between 0 and 1.0 and a reason for the score, considering 1.0 as a very relevant topic and 0 as an irrelevant topic. Your output should be a JSON for an object that represents the score and the reason. It should have the fields "score" and "reason" where "score" is a float and "reason" is a string.

            examples:

            Topic: Prevenção de reações químicas entre diferentes tipos de graxa
            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, não se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: {"score": 0.8, "reason": "O documento discute as potenciais consequências de misturar diferentes tipos de graxa em rolamentos, indicando uma relevância significativa para o tópico de prevenir reações químicas entre diferentes tipos de graxa."}
            Topic: Impacto do aperto excessivo da porca na vida útil do rolamento
            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, não se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: {"score": 1.0, "reason": "O documento aborda diretamente o impacto do aperto excessivo da porca na vida útil do rolamento, confirmando uma relação muito forte com o tópico proposto."}
            Topic: Funções e tipos de válvulas de motor
            Document: O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, não se deve substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: {"score": 0, "reason": "O documento não aborda funções ou tipos de válvulas de motor; portanto, não há relevância para o tópico proposto."}""",
            user_prompt="""
            Topic: {topic}
            Document: {document}
            Answer:""",
            variables=['topic', 'document']
        )
