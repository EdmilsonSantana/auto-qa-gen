from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase
from deepeval.metrics import BaseMetric
from model import BASE_MODEL
import numpy as np
import os
import asyncio


class MetricsEvaluationModel(DeepEvalBaseLLM):
    def __init__(self, model):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        return self.model.remote([prompt])[0]

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self):
        return BASE_MODEL


async def measure(
        metric: BaseMetric,
        test_input: str,
        scenario: dict,
        tests_results: list):
    test_case = LLMTestCase(
        input=test_input,
        context=[scenario['context']],
        actual_output=scenario['actual_output'])

    try:
        print(f"Measuring scenario {scenario}")

        await metric.a_measure(test_case)

        tests_results.append(
            dict(
                score=metric.score,
                reason=metric.reason,
                success=metric.success,
                context=test_case.context,
                actual_output=test_case.actual_output
            )
        )
    except Exception as error:
        print(f"Failed test case: {error}")
        tests_results.append(dict(
            score=0.0,
            reason=error,
            success=False,
            context=test_case.context,
            actual_output=test_case.actual_output
        ))


async def run_tests(test_input: str, metric: BaseMetric, test_scenarios: list, chunk_size: int = 5):
    os.environ["DISABLE_DEEPEVAL_INDICATOR"] = "YES"

    tests_results = []
    for chunk in np.array_split(test_scenarios, chunk_size):
        measures = [measure(metric, test_input, scenario, tests_results)
                    for scenario in chunk]
        await asyncio.gather(*measures)

    return tests_results
