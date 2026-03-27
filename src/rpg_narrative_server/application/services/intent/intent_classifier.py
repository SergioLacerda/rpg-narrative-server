
class IntentClassifier:

    def __init__(
        self,
        profiles,
        llm_classifier=None,
        *,
        threshold: float = 2.0,
    ):
        self.profiles = profiles
        self.llm = llm_classifier
        self.threshold = threshold

    # ---------------------------------------------------------
    # PUBLIC
    # ---------------------------------------------------------

    async def is_action(self, text: str) -> bool:
        score = await self.score(text)
        return score >= self.threshold

    async def score(self, text: str) -> float:
        text = self._normalize(text)

        if not text:
            return -10.0

        # ----------------------------------
        # BASE FEATURES
        # ----------------------------------

        score = 0.0

        if self._is_ooc(text):
            base = -5.0
            if self.llm:
                base += self._llm_score(await self.llm.classify(text))
            return base

        if self._is_too_short(text):
            return -2.0

        score += self._weak_penalty(text)
        score += self._trigger_score(text)
        score += self._length_score(text)

        # ----------------------------------
        # LLM BOOST (authoritative)
        # ----------------------------------

        if self.llm:
            try:
                result = await self.llm.classify(text)
                score += self._llm_score(result)

            except Exception:
                pass

        return score

    async def classify(self, text: str) -> str:

        score = await self.score(text)

        if score >= 4:
            return "ACTION"

        if score >= 2:
            return "EXPLORATION"

        if score <= -4:
            return "OOC"

        return "CHAT"

    # ---------------------------------------------------------
    # FEATURES
    # ---------------------------------------------------------

    def _normalize(self, text: str) -> str:
        return (text or "").strip().lower()

    def _is_ooc(self, text: str) -> bool:
        ooc_patterns = [
            "isso está", "isso nao", "isso não",
            "bug", "erro", "wtf", "lol", "kkk"
        ]

        if text.startswith("("):
            return True

        return any(p in text for p in ooc_patterns)

    def _is_too_short(self, text: str) -> bool:
        return len(text.split()) < 2

    def _weak_penalty(self, text: str) -> float:

        words = set(text.split())

        for profile in self.profiles:
            if words & set(profile.weak_words):
                return -1.0 

        return 0.0

    def _trigger_score(self, text: str) -> float:
        words = set(text.split())
        score = 0.0

        for profile in self.profiles:
            matches = words & set(profile.triggers)

            if matches:
                score += min(3.0, 2.0 * len(matches)) 

        return score

    def _length_score(self, text: str) -> float:

        words = len(text.split())

        if words >= 8:
            return 2.0

        if words >= 4:
            return 1.0

        if words >= 2:
            return 0.3

        return 0.0

    def _llm_score(self, result: str) -> float:

        if not result:
            return 0.0

        result = result.strip().upper()

        if result == "ACTION":
            return 2.0 

        if result == "OOC":
            return -2.0

        if result == "CHAT":
            return -1.0

        return 0.0