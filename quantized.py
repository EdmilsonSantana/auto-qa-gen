from typing import Optional, List, Dict
from datasets import Dataset
from awq import AutoAWQForCausalLM
from bonito import AbstractBonito
from transformers import AutoTokenizer


class QuantizedBonito(AbstractBonito):
    def __init__(self, model_name_or_path):
        self.model = AutoAWQForCausalLM.from_quantized(model_name_or_path, fuse_layers=True).cuda()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

    def generate_task(
        self,
        unannotated_paragraph: str,
        task_type: str,
        sampling_params: dict,
    ) -> Dict:
        """
        Generates synthetic instruction tuning pair using the Quantized Bonito model.
        This method takes a text unannotated text, a task type, and sampling parameters,
        and generates synthetic input-output pair.

        Args:
            unannotated_paragraph (str): The unannotated text or a paragraph
            task_type (str): The type of the tasks. This can be a
                short form or a full form.
            sampling_params (dict): The parameters for
                sampling.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict: The synthetic input-output pair for the task type.
        """

        text_dataset = Dataset.from_list([{"input": unannotated_paragraph}])

        processed_dataset = self._prepare_bonito_input(
            text_dataset, task_type, context_col="input"
        )

        outputs = self._generate_text(processed_dataset["input"], sampling_params)
        examples = []
        for i, example in enumerate(text_dataset.to_list()):
            output = outputs[i]
            example["prediction"] = output.strip()
            examples.append(example)

        synthetic_dataset = Dataset.from_list(examples)

        # filter out the examples that cannot be parsed
        synthetic_dataset_dict = self._postprocess_dataset(
            synthetic_dataset, context_col="input"
        ).to_list()[0]

        return synthetic_dataset_dict

    def _generate_text(
        self,
        dataset: Dataset,
        sampling_params: dict,
        ) -> List[str]:
        """
        Generate text using huggingface transformers generate function.

        This method takes a dataset of prompts, encodes them,
        generates text using the model, decodes the generated
        text, and appends it to a list.

        Args:
            dataset (Dataset): A dataset containing prompts for text generation.
            sampling_params (dict): Parameters for sampling during generation.

        Returns:
            List[str]: A list of generated texts corresponding to the prompts.
        """
        generated_texts = []

        for prompt in dataset:
            input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
            input_ids = input_ids.cuda()

            output = self.model.generate(
                input_ids,
                do_sample=True,
                **sampling_params
            )

            generated_text = self.tokenizer.decode(output[0][len(input_ids[0]):], skip_special_tokens=True)
            generated_texts.append(generated_text)

        return generated_texts