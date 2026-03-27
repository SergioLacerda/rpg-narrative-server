class ContextSelector:

    def __init__(self, max_tokens=2000, token_counter=None):
        self.max_tokens = max_tokens
        self.token_counter = token_counter or (lambda tokens: len(tokens))

    def select(self, docs, tokenizer):

        selected = []
        total_tokens = 0

        for doc in docs:

            text = self._extract_text(doc)

            tokens = tokenizer.tokenize(text)
            token_count = self.token_counter(tokens)

            if total_tokens + token_count > self.max_tokens:
                break

            selected.append(doc)
            total_tokens += token_count

        return selected

    # ---------------------------------------------------------
    # utils
    # ---------------------------------------------------------

    def _extract_text(self, doc):

        if isinstance(doc, str):
            return doc

        if isinstance(doc, dict):
            return doc.get("text", "")

        return str(doc)