from .internlm import InternLM
from . import IModel


class ModelFactory:
    @staticmethod
    def create(local=False) -> IModel:
        if not local:
            return InternLM()
        pass
