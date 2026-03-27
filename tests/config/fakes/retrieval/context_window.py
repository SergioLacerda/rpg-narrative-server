class DummyContextWindow:
    def __init__(self):
        self.policy_called_with = None
        self.apply_called_with = None

    def get_policy(self, query):
        self.policy_called_with = query
        return {"limit": 1}

    def apply(self, docs, policy):
        self.apply_called_with = (docs, policy)
        return docs[:1]
