# Automotive Q&A Generator

Esse repositório contém os artefatos produzidos no trabalho de conclusão de curso "IA Generativa Aplicada a Capacitação do Setor Automotivo".

## Extraindo Q&A a partir de documentos

### Fontes de dados

As apostilas utilizadas se encontram no diretório `data/source` e os arquivos json gerados no processo de extração das questões podem ser encontrados em `data/output`.

#### Preparação dos documentos

As apostilas foram cedidas pela [Universidade do Automóvel](https://www.universidadedoautomovel.com.br/) em formato DOCX. Foi utilizado o pacote [python-docx](https://python-docx.readthedocs.io/en/latest/) para realizar a leitura do conteúdo das apostilas. O conteúdo foi agrupado por seção e seções como capa, sumário, introdução e referências bibliográficas não foram consideradas, assim como legendas de figuras e tabelas. O conteúdo obtido foi exportado no formato .json no arquivo `data/source/documents.json` e o código utilizado para processamento das apostilas encontra-se em `src/documents`.

### Processo de extração das questões

#### Implantação e execução do modelo

Para extrair as questões das apostilas foi utilizado o modelo [InternLM2](https://huggingface.co/internlm/internlm2-chat-7b) em sua versão de chat com 7 bilhões de parâmetros. É um modelo de código aberto, que permite uso acadêmico e comercial, e que apresenta uma das melhores performances nos benchmarks da lingua portuguesa no [Open Portuguese LLM](https://huggingface.co/spaces/eduagarcia/open_pt_llm_leaderboard), considerando apenas os modelos com a mesma quantidade de parâmetros. O modelo foi implantado na cloud do [Modal](https://modal.com/) como uma aplicação serverless e foi utilizado o [vLLM](https://github.com/vllm-project/vllm) para otimizar o desempenho da execução de inferência do modelo. O código utilizado para implantação do modelo encontra-se em `src\models\internlm.py`

#### Prompt engineering

O processo de extração das questões consiste de múltiplas etapas, onde em cada etapa é executado um prompt no modelo, sendo estes de dois tipos: extração e validação. Prompts de extração buscam obter algum dado específico dos documentos, enquanto os de validação usam o documento como referência para validar se a extração ocorreu com sucesso, seguindo alguma regra de validação definida no prompt. Essa estratégia de validação é inspirada no framework [DeepEval](https://github.com/confident-ai/deepeval), porém o mesmo não foi utilizado por não dar suporte ao vLLM.

O processo se inicia com a extração de tópicos a partir do conteúdo dos documentos, com o objetivo de direcionar a extração de questões para temas específicos. Os tópicos extraidos são validados e os que tem fraca relação com o documento são descartados. Para cada tópico obtido, são extraídas questões e respostas referentes ao tópico e ao documento o qual ele pertence. Por fim, as questões que são pouco relacionadas ao documento são descartadas, assim como aquelas que possuem respostas erradas.
Os prompts utilizados estão disponíveis em `src\prompts`.

### Executando processo

Pré-requisitos

- Instalar o pacote [python_docx](https://pypi.org/project/python-docx/);
- Criar uma conta na plataforma Modal e seguir o passo a passo disponível em: https://modal.com/docs/guide#getting-started;
  - O uso do Modal não é obrigatório e é possível utilizar outro modelo implementando a classe `IModel` disponível em `src\models\__init__.py` e alterando o modelo em `src\index.py`.

Por fim execute:
```
python src/index.py
```

O arquivo `vehicle_repair_and_maintenance_qa.json` é gerado no final do processo e utilizado como dataset para fine-tuning do modelo. 


## Fine-Tuning do modelo PPT5

O fine-tuning foi realizado no modelo [PTT5](https://huggingface.co/unicamp-dl/ptt5-base-portuguese-vocab), modelo  pré-treinado do Google T5 com o vocabulário da língua portuguesa. O treinamento e avaliação do modelo estão acessíveis neste [notebook](notebooks/PTT5_Fine_Tuning.ipynb) e o modelo encontra-se disponível no [Hugging Face](https://huggingface.co/emgs/ptt5-qa).
