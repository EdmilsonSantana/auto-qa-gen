from models import IModel
from . import PromptRequest, PromptTemplate, PromptHandler, PromptValidationHandler
import uuid


class TopicsExtractionPrompt(PromptHandler):
    def __init__(self, model: IModel, subject: str, number_of_topics: int = 5) -> None:
        super().__init__(model)
        self.subject = subject
        self._number_of_topics = number_of_topics

    def get_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            name="topics",
            system_prompt=f"""
            Given a document your goal is to extract {self._number_of_topics} topics that summarizes the content present in the document.
            Here are some criterias that you have to follow to achieve your goal:

            - The topics should be extracted in the same language as the document.
            - You should not extract topics not related to {self.subject}.
            - You should not extract short topics.
            - The output should be a JSON list of strings in the following format: ["topic", "topic", "topic"].
            - If there is not enough content to generate topics your output should be a empty list: [].

            examples:

            Document: O cuidado com o meio ambiente é uma preocupação global imprescindível para o desenvolvimento sustentável. No mundo dos automóveis, essa discussão é cada vez maior, com o aumento do rigor na legislação em diversos países - o que acelera a evolução de veículos de propulsão alternativa, como híbridos e elétricos. O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: [\"A importância global do cuidado com o meio ambiente\", \"A evolução dos veículos de propulsão alternativa\", \"O aumento da legislação ambiental nos países\", \"Impacto do aperto excessivo da porca na vida útil do rolamento\", \"Cuidados específicos com a manutenção de rolamentos dianteiros selados\"]
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
            Given a document and a topic, classify how related the topic is to the document with a score between 0 and 1.0 and a reason for the score, considering 1.0 as a very related topic and 0 as an unrelated topic. Your output should be a JSON for an object that represents the score and the reason. It should have the fields "score" and "reason" where "score" is a float and "reason" is a string.

            examples:

            Topic: A importância global do cuidado com o meio ambiente
            Document: O cuidado com o meio ambiente é uma preocupação global imprescindível para o desenvolvimento sustentável. No mundo dos automóveis, essa discussão é cada vez maior, com o aumento do rigor na legislação em diversos países - o que acelera a evolução de veículos de propulsão alternativa, como híbridos e elétricos. O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: {"score": 1.0, "reason": "O tópico do cuidado ambiental é abordado diretamente no documento. A discussão sobre o desenvolvimento de veículos de propulsão alternativa na indústria automotiva é citada como uma consequência das preocupações ambientais globais. Portanto, o tópico está altamente relacionado ao documento."}
            Topic: Recomendações do grupo Schaeffler
            Document: O cuidado com o meio ambiente é uma preocupação global imprescindível para o desenvolvimento sustentável. No mundo dos automóveis, essa discussão é cada vez maior, com o aumento do rigor na legislação em diversos países - o que acelera a evolução de veículos de propulsão alternativa, como híbridos e elétricos. O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: {"score": 0.1, "reason": "Embora o texto mencione Airton da Schaeffler, o foco principal está nas preocupações ambientais e seu impacto no desenvolvimento automotivo. As recomendações do grupo Schaeffler não são o tema central, resultando em uma pontuação baixa de relevância."}
            Topic: Funções e tipos de válvulas de motor
            Document: O cuidado com o meio ambiente é uma preocupação global imprescindível para o desenvolvimento sustentável. No mundo dos automóveis, essa discussão é cada vez maior, com o aumento do rigor na legislação em diversos países - o que acelera a evolução de veículos de propulsão alternativa, como híbridos e elétricos. O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
            Answer: {"score": 0, "reason": "O tópico das funções e tipos de válvulas de motor não é mencionado ou sugerido no documento fornecido. Portanto, está sem relação, resultando em uma pontuação de 0."}""",
            user_prompt="""
            Topic: {topic}
            Document: {document}
            Answer:""",
            variables=['topic', 'document']
        )
