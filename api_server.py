import time

import uvicorn
from argparse import ArgumentParser
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from msg_defs import ChatRequest, ChatResponse
from models import StarCoderGenerator

app = FastAPI()
app.add_middleware(CORSMiddleware)

generator: StarCoderGenerator = ...


@app.post("/api/chat/completion")
async def code_completion(request: Request):
    try:
        json_request = await request.json()
        chat_request = ChatRequest(**json_request)

        tic = time.time()
        generated_text = generator.generate(
            chat_request
        )
        toc = time.time()

        return ChatResponse(
            generated_text=generated_text,
            api_response_time=round(toc - tic, 2),
            status_code=200,
            error_message=None
        )
    except Exception as e:
        return ChatResponse(
            generated_text="",
            api_response_time=None,
            status_code=500,
            error_message=e.__repr__()
        )


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
