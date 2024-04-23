from .modal import RemoteModalModel
from .model import IModel


class ModelFactory:
    @staticmethod
    def create(model_name: str, local=False) -> IModel:
        if not local:
            return RemoteModalModel(model_name)
        """TODO support local models"""
        pass
