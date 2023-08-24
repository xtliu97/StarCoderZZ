import logging

import uvicorn
from argparse import ArgumentParser
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from msg_defs import ChatRequest, ChatResponse
from models import StarCoderGenerator

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(CORSMiddleware)

generator: StarCoderGenerator = ...


@app.post("/code/completion")
async def code_completion(request: Request) -> ChatResponse:

    json_request = await request.json()
    chat_request = ChatRequest(**json_request)
    logging.info(f"Received request:\n {chat_request}")

    chat_response = generator.get_response(chat_request)

    if chat_response.status_code == 200:
        logging.info(f"Generated text:\n {chat_response.generated_text}")
    elif chat_response.status_code == 500:
        logging.error(f"Error message:\n {chat_response.error_message}")

    return chat_response


@app.post("/chat/completion")
async def chat_completion(request: Request) -> ChatResponse:
    json_request = await request.json()
    chat_request = ChatRequest(**json_request)
    logging.info(f"Received request:\n {chat_request}")

    chat_response = generator.get_chat_response(chat_request)

    if chat_response.status_code == 200:
        logging.info(f"Generated text:\n {chat_response.generated_text}")
    elif chat_response.status_code == 500:
        logging.error(f"Error message:\n {chat_response.error_message}")

    return chat_response


@app.post("/code/completion/stream")
async def code_completion_stream(request: Request) -> ChatResponse:
    pass


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--host", type=str, default="localhost")
    arg_parser.add_argument("--port", type=int, default=8000)
    arg_parser.add_argument("--model", type=str, required=True)
    args = arg_parser.parse_args()

    global generator
    generator = StarCoderGenerator(args.model)

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
