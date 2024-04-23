from document import DocumentCollection
from constants import SECTIONS_TO_IGNORE
from model.factory import ModelFactory

RAW_DIR = './raw_data'

collection = DocumentCollection(RAW_DIR, SECTIONS_TO_IGNORE)

print(collection.get_documents()[0])

#collection.save('./data_2')

model = ModelFactory.create('llm-inference')

model.generate()


# criar interface para o modelo
# criar nova classe para representar um gerador de topics ou questoes que recebe o modelo e os documentos
# o gerador tem 3 fases: extração, validação e reflexão
