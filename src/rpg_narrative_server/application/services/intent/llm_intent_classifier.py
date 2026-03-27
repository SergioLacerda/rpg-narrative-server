from rpg_narrative_server.application.dto.llm_request import LLMRequest


class LLMIntentClassifier:
    def __init__(self, llm_factory):
        self._llm_factory = llm_factory
        self._llm = None

    # ---------------------------------------------------------

    def _get_llm(self):
        if self._llm is None:
            self._llm = self._llm_factory()
        return self._llm

    # ---------------------------------------------------------
    # 🔥 heurística leve (rápida e barata)
    # ---------------------------------------------------------

    def _rule_based(self, text: str) -> str | None:
        t = text.lower()

        # ação típica de RPG
        if any(
            w in t for w in ["ataco", "olho", "corro", "entro", "pego", "investigo"]
        ):
            return "ACTION"

        # chat casual
        if any(w in t for w in ["oi", "ola", "kk", "haha", "fala", "mano"]):
            return "CHAT"

        return None

    # ---------------------------------------------------------

    async def classify(self, text: str) -> str:
        rule = self._rule_based(text)
        if rule:
            return rule

        llm = self._get_llm()

        system_prompt = """
Você é um classificador de intenções para um RPG.

Classifique a mensagem do jogador em UMA categoria:

- ACTION → ação dentro do jogo
- CHAT → conversa casual
- OOC → fora do jogo

Exemplos:
"ataco o goblin" → ACTION
"oi tudo bem?" → CHAT
"isso não faz sentido" → OOC

Responda apenas com UMA palavra:
ACTION, CHAT ou OOC

Nunca explique.
""".strip()

        request = LLMRequest(
            system_prompt=system_prompt,
            prompt=text,
            temperature=0.0,
            max_tokens=5,
        )

        try:
            response = await llm.generate(request)

            if not response:
                return "CHAT"

            result = response.strip().upper()

            result = result.replace("\n", " ").strip()

            if result in ("ACTION", "CHAT", "OOC"):
                return result

            if "ACTION" in result:
                return "ACTION"

            if "OOC" in result:
                return "OOC"

            if "CHAT" in result:
                return "CHAT"

            return "CHAT"

        except Exception:
            return "CHAT"
