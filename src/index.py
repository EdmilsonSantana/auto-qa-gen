from documents import DocumentCollection
from utils.constants import SECTIONS_TO_IGNORE
from models.factory import ModelFactory
from prompts.topics import TopicsExtractionPrompt, TopicsValidationPrompt
from prompts.qa import QuestionAnswerExtractionPrompt, QuestionsValidationPrompt, AnswerValidationPrompt, QuestionAnswerVariationsPrompt
from prompts import PromptRequest
from utils import config_log, save_json
from utils.constants import SOURCE_DIR, OUTPUT_DIR

config_log()

collection = DocumentCollection(SOURCE_DIR, SECTIONS_TO_IGNORE)

collection.save(OUTPUT_DIR)

model = ModelFactory.create(local=False)

requests = [
    PromptRequest(
        metadata=dict(document_id=document['document_id'],
                      section=document['section']),
        data=dict(document=document['content'])
    ) for document in collection.to_dict()]

subject = 'vehicle repair and maintenance'

prompt = TopicsExtractionPrompt(model, subject)
prompt.set_next(TopicsValidationPrompt(model)) \
    .set_next(QuestionAnswerExtractionPrompt(model, subject)) \
    .set_next(QuestionAnswerVariationsPrompt(model)) \
    .set_next(QuestionsValidationPrompt(model, 0.7)) \
    .set_next(AnswerValidationPrompt(model, 0.7))

qa_dataset = prompt.handle(requests, batch_size=50)

filename = 'vehicle_repair_and_maintenance_qa.json'
save_json(f'{OUTPUT_DIR}/{filename}', qa_dataset, append=True)
