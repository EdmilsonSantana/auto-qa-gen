class IModel:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.lodal_model()

    """Load model parameters to be able to execute 'generate' method."""
    def lodal_model() -> None:
        pass

    """Generate a list of responses given a system prompt and multiple user prompts."""
    def generate(self, system_prompt: str, user_prompts: list[str]) -> list[str]:
        pass
