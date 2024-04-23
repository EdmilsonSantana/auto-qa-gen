n_topics = 5

topics_system_prompt = f"""
Given a document your goal is to extract {n_topics} topics that summarizes the content present in the document.
Here are some criterias that you have to follow to achieve your goal:

- The topics should be extracted in the same language as the document.
- You should not extract topics not related to vehicle repair and maintenance.
- You should not extract short topics.
- The output should be a JSON list of strings in the following format: ["topic", "topic", "topic"].

examples:

Document: O cuidado com o meio ambiente é uma preocupação global imprescindível para o desenvolvimento sustentável. No mundo dos automóveis, essa discussão é cada vez maior, com o aumento do rigor na legislação em diversos países - o que acelera a evolução de veículos de propulsão alternativa, como híbridos e elétricos. O aperto excessivo da porca afeta diretamente a vida útil do rolamento. Em rolamentos dianteiros selados, Airton, da Schaeffler, adverte para nunca substituir a graxa ou completar os espaços internos, porque pode haver uma reação entre as graxas com composições químicas diferentes, além de um aquecimento elevado no interior do rolamento.
Answer: [\"A importância global do cuidado com o meio ambiente\", \"A evolução dos veículos de propulsão alternativa\", \"O aumento da legislação ambiental nos países\", \"Impacto do aperto excessivo da porca na vida útil do rolamento\", \"Cuidados específicos com a manutenção de rolamentos dianteiros selados\"]
Document: Entre os vários parâmetros levados em conta no projeto da suspensão de um carro, os três principais ângulos medidos no alinhamento de veículos leves são convergência e divergência (paralelismo horizontal entre as rodas), câmber (ângulo de inclinação lateral da roda em relação ao eixo vertical) e o cáster (inclinação do eixo vertical referente ao centro da circunferência da roda). Mas antes de instalar o equipamento de medição, o primeiro procedimento que o mecânico deve fazer é analisar os sintomas.
Answer: [\"Parâmetros essenciais no projeto da suspensão de um carro\", \"Importância da análise dos sintomas antes da medição\", \"Convergência e divergência: impacto no alinhamento das rodas\", \"Câmber: influência do ângulo de inclinação lateral da roda\", \"Cáster: considerações sobre a inclinação do eixo vertical\"]"""

topics_user_prompt = """
Document: {document}
Answer:"""