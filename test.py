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

    def test_llama_cpp_api(self):
        API_URL = "http://localhost:8080/completion"
        import requests
        input = {
            "prompt": "def quicksort(arr):",
            "n_predict": 100,
        }
        response = requests.post(API_URL, json=input)
        print(response.json()['content'])


if __name__ == '__main__':
    unittest.main()
