# init_client, LLM_CFG
import os
from typing import Dict
from utils.easonsi.llm.openai_client import OpenAIClient

LLM_CFG = {}
def add_openai_models():
    global LLM_CFG
    model_list = [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4",
        "openai/gpt-oss-20b",
        # ── Local models qua LM Studio ──────────────────────────────────
        "openai/qwen2.5-3b-instruct",
        "openai/qwen2.5-7b-instruct",
        "openai/llama-3.2-3b-instruct",
        "openai/llama-3-8b-instruct",
        "openai/phi-3.5-mini-instruct",
    ]
    for model in model_list:
        assert model not in LLM_CFG, f"{model} already in LLM_CFG"
        LLM_CFG[model] = {
            "model_name": model,
            "base_url": os.getenv("OPENAI_BASE_URL"),
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
add_openai_models()


def init_client(llm_cfg: Dict):
    client = OpenAIClient(
        model_name=llm_cfg["model_name"], base_url=llm_cfg["base_url"], api_key=llm_cfg["api_key"]
    )
    return client