from abc import ABC, abstractmethod
from models import IModel
from dataclasses import dataclass, replace
from utils import load_json, save_json, chunker
from typing import Self
import logging
from pathlib import Path
import time
import re

from utils.constants import OUTPUT_DIR

CHECKPOINTS_DIR = f'{OUTPUT_DIR}/checkpoints'


@dataclass
class PromptTemplate:
    name: str
    system_prompt: str
    user_prompt: str
    variables: list

    def format(self, args: dict):
        return self.user_prompt.format(**{var: args[var] for var in self.variables})


@dataclass
class PromptRequest:
    metadata: dict
    data: dict

    def update(self, data: dict, metadata: dict):
        return PromptRequest(
            metadata={**self.metadata, **metadata},
            data={**self.data, **data})


@dataclass
class PromptValidationRequest:
    request: PromptRequest
    score: float
    reason: str


@dataclass
class FailedPromptRequest:
    request: PromptRequest
    response_data: str
    error: Exception


class PromptHandler(ABC):
    _next_handler: Self = None
    _model: IModel = None
    _logger = logging.getLogger(__name__)

    def __init__(self, model: IModel) -> None:
        self._model = model
        self.max_retries = 10

    def set_next(self, handler: Self) -> Self:
        self._next_handler = handler
        return handler

    def handle(self, requests: list[PromptRequest], batch_size: int = 100) -> list[PromptRequest]:
        self._logger.info(f"Starting '{self.__get_name()}' prompt template")
        successful_requests = []
        requests_count = len(requests)
        processed_count = 0
        for batch_requests in chunker(requests, batch_size):
            processed_count += len(batch_requests)
            self._logger.info(
                f"Processing {processed_count} / {requests_count}")

            for i in range(1, self.max_retries + 1):
                batch_successful_requests, batch_error_requests = self.generate(
                    requests=batch_requests
                )

                successful_requests.extend(batch_successful_requests)

                if len(batch_error_requests) == 0:
                    break

                if (i < self.max_retries):
                    batch_requests = [error_request.request
                                      for error_request in batch_error_requests]
                    self._logger.info(
                        f"Retrying ({i}/{self.max_retries}) {len(batch_requests)} request(s)")
                else:
                    self._logger.info(
                        f"Found {len(batch_error_requests)} error(s)")
                    self.save_checkpoint(
                        batch_error_requests, suffix='__error')

        self.save_checkpoint(successful_requests)

        self._logger.info(f"Finished '{self.__get_name()}' prompt template")

        if self._next_handler and len(successful_requests) > 0:
            self._logger.info("Calling next handler")
            return self._next_handler.handle(successful_requests)

        return successful_requests

    def generate(self, requests: list[PromptRequest]) -> tuple[list[PromptRequest], list[FailedPromptRequest]]:
        prompt_template = self.get_prompt_template()
        user_prompts = [prompt_template.format(request.data)
                        for request in requests]
        response = self._model.generate(
            prompt_template.system_prompt, user_prompts)
        error_requests = []
        successful_requests = []
        for response_data, request in zip(response, requests):
            try:
                obj = self.to_object(load_json(response_data), request)
                if len(obj) > 0:
                    successful_requests.extend(obj)
            except Exception as error:
                error_requests.append(FailedPromptRequest(
                    request, response_data, error))
        return successful_requests, error_requests

    def __get_name(self) -> str:
        return self.get_prompt_template().name

    def save_checkpoint(self, data: list[object], suffix=''):
        Path(CHECKPOINTS_DIR).mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        filename = re.sub(r'(?<!^)(?=[A-Z])', '_', self.__get_name()).lower()
        checkpoint_file = f'{CHECKPOINTS_DIR}/{filename}{suffix}_{ts}.json'
        save_json(checkpoint_file, data)

    @abstractmethod
    def get_prompt_template() -> PromptTemplate:
        pass

    @abstractmethod
    def to_object(self, json: dict | list, request: PromptRequest) -> list[PromptRequest]:
        pass


class PromptValidationHandler(PromptHandler):
    def __init__(self, model: IModel, score_threshold: float = 0.5) -> None:
        super().__init__(model)
        self._score_threshold = score_threshold

    def handle(self, requests: list[PromptRequest], batch_size: int = 100) -> list[PromptRequest]:
        next_handler = self._next_handler
        self._next_handler = None

        validation_requests = super().handle(requests, batch_size)

        successful_requests = []
        failed_validations = []
        for validation in validation_requests:
            if validation.score >= self._score_threshold:
                successful_requests.append(validation.request)
            else:
                failed_validations.append(validation)

        self.save_checkpoint(successful_requests, suffix='__passed')

        if (len(failed_validations) > 0):
            self.save_checkpoint(failed_validations, suffix='__failed')

        if next_handler and len(successful_requests) > 0:
            self._logger.info("Calling next handler")
            return next_handler.handle(successful_requests)

        return successful_requests

    def to_object(self, json: dict | list, request: PromptRequest) -> list[PromptRequest]:
        return [PromptValidationRequest(
            request=request,
            score=json.get('score', 0.0),
            reason=json.get('reason', None))]
