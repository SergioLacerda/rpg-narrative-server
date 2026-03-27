class FakeChoice:
    def __init__(self, content):
        self.message = type("Msg", (), {"content": content})


class FakeResponseOpenAI:
    def __init__(self, content="ok"):
        self.choices = [FakeChoice(content)]
        self.usage = type("Usage", (), {
            "prompt_tokens": 10,
            "completion_tokens": 20,
        })


class FakeResponseEmpty:
    def __init__(self):
        self.choices = []


class FakeOllamaResponse:
    def __init__(self, content="ok"):
        self._content = content

    def json(self):
        return {"response": self._content}