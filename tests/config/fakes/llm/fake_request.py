class DummyRequest:
    def __init__(self, prompt="hello", system_prompt="sys", temperature=0.0, max_tokens=100):
        self.prompt = prompt
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
