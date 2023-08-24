import os
import signal

from msg_defs import ChatRequest, ChatResponse
from chat_prompt import CHAT_PROMPT

from transformers import AutoModelForCausalLM, PreTrainedModel, AutoTokenizer, StoppingCriteriaList, StoppingCriteria


class KeywordsStoppingCriteria(StoppingCriteria):
    def __init__(self, keywords):
        self.keywords = keywords
        print(keywords)

    def __call__(self, input_ids, scores, **kwargs):
        for keyword in self.keywords:
            if input_ids[0][-1] == keyword:
                return True
        return False


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return ChatResponse(
                generated_text="",
                api_response_time=None,
                status_code=500,
                error_message=e.__repr__()
            )
    return wrapper


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

    @exception_handler
    def get_response(self, chat_request: ChatRequest) -> ChatResponse:
        inputs = self.tokenizer.encode(
            chat_request.inputs, return_tensors="pt").to(self.device)
        parameters = chat_request.parameters
        temperature = parameters.temperature
        top_k = parameters.top_k
        top_p = parameters.top_p
        max_new_tokens = parameters.max_new_tokens
        max_time = parameters.max_time if parameters.max_time != None else 1000

        # set a timeout handler
        def timeout_handler(signum, frame):
            raise TimeoutError(
                "Max time {}s exceeded, may be you can set a larger max_time".format(max_time))

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(max_time)
        try:
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
        except TimeoutError as e:
            raise e
        finally:
            signal.alarm(0)

        generated_text = self.tokenizer.decode(
            generated_ids[0], skip_special_tokens=False, clean_up_tokenization_spaces=False)
        return ChatResponse(
            generated_text=generated_text,
            api_response_time=None,
            status_code=200,
            error_message=None
        )

    @exception_handler
    def get_chat_response(self, request: ChatRequest) -> ChatResponse:
        inputs_with_prompt = CHAT_PROMPT.strip() + "\n\nHuman:" + \
            request.inputs + "\n\nAssistant:"
        inputs = self.tokenizer.encode(
            inputs_with_prompt, return_tensors="pt").to(self.device)

        parameters = request.parameters
        max_new_tokens = 2000  # bigger for chat, parameters.max_new_tokens
        temperature = parameters.temperature
        top_k = parameters.top_k
        top_p = parameters.top_p
        max_time = parameters.max_time if parameters.max_time != None else 1000
        truncate = 8000
        repeat_penalty = 1.2
        stop_criteria_keywords = ["-----",  "Assistant:"]
        stop_criteria = KeywordsStoppingCriteria(
            [self.tokenizer.encode(keyword)[0]
             for keyword in stop_criteria_keywords]
        )
        generated_ids = self.model.generate(
            inputs,
            do_sample=True,
            min_length=10,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            # max_time=max_time,
            stopping_criteria=StoppingCriteriaList([stop_criteria]),
            repetition_penalty=repeat_penalty,
            pad_token_id=0,

        )
        target_ids = generated_ids[0][len(inputs[0]):]
        print(target_ids)
        generated_text = self.tokenizer.decode(
            target_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False, truncate_text=True)

        return ChatResponse(
            generated_text=generated_text,
            api_response_time=None,
            status_code=200,
            error_message=None
        )

    @exception_handler
    def get_response_stream(self, request: ChatRequest) -> ChatResponse:
        pass
