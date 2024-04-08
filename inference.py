import os
from modal import Image, Secret, Stub, enter, exit, gpu, method
import json

MODEL_DIR = "/model"
BASE_MODEL = "Qwen/Qwen1.5-7B-Chat"

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
        "accelerate"
    )
    # Use the barebones hf-transfer package for maximum download speeds. Varies from 100MB/s to 1.5 GB/s,
    # so download times can vary from under a minute to tens of minutes.
    # If your download slows down or times out, try interrupting and restarting.
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
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if GPU_CONFIG.count > 1:
            # Patch issue from https://github.com/vllm-project/vllm/issues/1116
            import ray

            ray.shutdown()
            ray.init(num_gpus=GPU_CONFIG.count)

        self.template = (
            "start_of_turn>user\n{user}<end_of_turn>\n<start_of_turn>model"
        )
    
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_DIR,
            torch_dtype="auto",
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

    @method()
    def generate(self, system_prompt, user_input):
        import time

        start = time.monotonic_ns()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        model_inputs = self.tokenizer([text], return_tensors="pt").to("cuda")

        generated_ids = self.model.generate(
            model_inputs.input_ids,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
   
        duration_s = (time.monotonic_ns() - start) / 1e9

        print(f"Duration: {duration_s}")

        return response

    @exit()
    def stop_engine(self):
        if GPU_CONFIG.count > 1:
            import ray

            ray.shutdown()
