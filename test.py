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

    def test_api(self):
        API_URL = "http://localhost:8000/api/chat/completion"
        demo_request = ChatRequest(
            inputs="def quicksort(arr):",
        )
        response = get_response(API_URL, demo_request)
        print(response.generated_text)


if __name__ == '__main__':
    unittest.main()
