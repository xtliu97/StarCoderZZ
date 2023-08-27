import unittest

from msg_defs import ChatRequest, get_response
from models import StarCoderGenerator


class TestGenerator(unittest.TestCase):
    # def test_generator(self):
    #     model = StarCoderGenerator("model")
    #     chat_request = ChatRequest(
    #         inputs="def quicksort(arr):",
    #     )
    #     print(model.generate(chat_request))

    # def test_api(self):
    #     API_URL = "http://localhost:8000/api/chat/completion"
    #     demo_request = ChatRequest(
    #         inputs="def quicksort(arr):",
    #     )
    #     response = get_response(API_URL, demo_request)
    #     print(response.generated_text)

    # def test_llama_cpp_api(self):
    #     API_URL = "http://localhost:8000/code/completion"
    #     import requests
    #     input = {
    #         "inputs": "def quicksort(arr):",
    #         "parameters": {
    #             "temperature": 1.0,
    #             "max_new_tokens": 200,
    #         }
    #     }
    #     response = requests.post(API_URL, json=input)
    #     print(response.json()['generated_text'])

    def test_chat_api(self):
        API_URL = "http://localhost:8000/chat/completion"
        import requests
        input = {
            "inputs": "Write a function to sort a list of integers in ascending order.",
            "parameters": {
                "temperature": 0.2,
                "top_p": 0.9,
                "max_new_tokens": 2000,
            }
        }
        response = requests.post(API_URL, json=input)
        print(response.json()['generated_text'])


if __name__ == '__main__':
    unittest.main()
