import requests
import time

from typing import Optional
from pydantic import BaseModel


class ModelParameter(BaseModel):
    temperature: float = 1.0
    top_k: int | None = None
    top_p: float | None = None
    max_new_tokens: int | None = 300
    max_time: float | None = None


class ChatRequest(BaseModel):
    inputs: str
    parameters: ModelParameter = ModelParameter()


class ChatResponse(BaseModel):
    generated_text: str
    api_response_time: Optional[float] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None


def get_response(url: str, request: ChatRequest) -> ChatResponse:
    serialized_request = request.model_dump()
    tic = time.time()
    ret = requests.request("POST", url, json=serialized_request)
    toc = time.time()
    response_time = round(toc - tic, 2)
    try:
        generated_text = ret.json()["generated_text"]
        error_msg = None
    except Exception as e:
        generated_text = ""
        error_msg = e.__repr__()

    return ChatResponse(
        generated_text=generated_text,
        api_response_time=response_time,
        status_code=ret.status_code,
        error_message=error_msg
    )


if __name__ == "__main__":
    import requests
    API_URL = "https://api-inference.huggingface.co/models/gpt2"
    demo_request = ChatRequest(
        inputs="The capital of France is",
        parameters=ModelParameter()
    )
    response = get_response(API_URL, demo_request)
    print(response)
