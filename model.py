import os
from modal import Image, Secret, Stub, enter, gpu, method

MODEL_DIR = "/model"
BASE_MODEL = "internlm/internlm2-chat-7b"


def download_model_to_folder():
    from huggingface_hub import snapshot_download
    from transformers.utils import move_cache

    os.makedirs(MODEL_DIR, exist_ok=True)

    snapshot_download(
        BASE_MODEL,
        local_dir=MODEL_DIR,
        token=os.environ["HF_TOKEN"],
        ignore_patterns=["*.pt", "*.gguf"],
    )
    move_cache()


image = (
    Image.from_registry(
        "nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.10"
    )
    .pip_install(
        "vllm==0.3.2",
        "huggingface_hub==0.19.4",
        "hf-transfer==0.1.4",
        "torch==2.1.2",
        "accelerate",
        "einops"
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    .run_function(
        download_model_to_folder,
        secrets=[Secret.from_name("huggingface-secret")],
        timeout=60 * 20,
    )
)

stub = Stub("llm-inference", image=image)
GPU_CONFIG = gpu.A100(count=1)


@stub.cls(gpu=GPU_CONFIG, secrets=[Secret.from_name("huggingface-secret")])
class Model:
    @enter()
    def load(self):
        import vllm

        self.llm = vllm.LLM(
            MODEL_DIR,
            enforce_eager=True,  # skip graph capturing for faster cold starts
            tensor_parallel_size=GPU_CONFIG.count,
            trust_remote_code=True
        )
        self.template = """<s><|im_start|>system\n{system_prompt}<|im_end|>\n"""
        self.template += """<|im_start|>user\n{query}<|im_end|>\n<|im_start|>assistant\n"""

    @method()
    def generate(self, system_prompt, prompts_list):
        import time
        import vllm

        end_token = '<|im_end|>'
        tokenizer = self.llm.llm_engine.tokenizer.tokenizer
        sampling_params = vllm.SamplingParams(
            temperature=0.7,
            top_p=0.9,
            max_tokens=2048,
            skip_special_tokens=False,
            stop_token_ids=[tokenizer.eos_token_id,
                            tokenizer.convert_tokens_to_ids([end_token])[0]]
        )

        start = time.monotonic_ns()

        tokezined_prompts = []
        for prompt in prompts_list:
            tokezined_prompts.append(
                self.template.format(system_prompt=system_prompt, query=prompt))

        result = self.llm.generate(tokezined_prompts, sampling_params)

        response = []
        for output in result:
            decoded_output = tokenizer.decode(
                output.outputs[0].token_ids, skip_special_tokens=True)
            decoded_output = decoded_output.split("<|im_end|>")[0]
            response.append(decoded_output)

        duration_s = (time.monotonic_ns() - start) / 1e9

        print(f"Duration: {duration_s}")

        return response
