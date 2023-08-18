import os
import sys

from msg_defs import ChatRequest, ChatResponse

from transformers import AutoModelForCausalLM, PreTrainedModel, AutoTokenizer


class StarCoderGenerator:
    def __init__(self, model_name, device="cpu"):
        self.model_name = model_name
        self.device = device
        # only load local model, check path first
        if not os.path.exists(model_name):
            raise ValueError(f"Model {model_name} not found")
        self.model: PreTrainedModel = AutoModelForCausalLM.from_pretrained(
            model_name, trust_remote_code=True).to(device)
        self.model.eval()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def generate(self, chat_request: ChatRequest) -> str:
        inputs = self.tokenizer.encode(
            chat_request.inputs, return_tensors="pt").to(self.device)
        parameters = chat_request.parameters
        temperature = parameters.temperature
        top_k = parameters.top_k
        top_p = parameters.top_p
        max_new_tokens = parameters.max_new_tokens
        max_time = parameters.max_time

        generated_ids = self.model.generate(
            inputs,
            do_sample=True,
            min_length=0,
            max_length=len(inputs[0]) + max_new_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            max_time=max_time,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        generated_text = self.tokenizer.decode(
            generated_ids[0], skip_special_tokens=True)
        return generated_text
