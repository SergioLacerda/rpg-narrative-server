class NarrativeBuilder:

    # ---------------------------------------------------------
    # SYSTEM PROMPT
    # ---------------------------------------------------------

    def build_system_prompt(self, scene_type: str = "DEFAULT") -> str:

        scene_type = self._normalize_scene(scene_type)

        base = (
            "Você é um mestre de RPG narrativo.\n\n"
            "REGRAS:\n"
            "- Nunca diga \"OOC\"\n"
            "- Nunca explique regras\n"
            "- Nunca controle o jogador\n\n"
        )

        return base + self._get_style(scene_type)

    # ---------------------------------------------------------
    # USER PROMPT (🔥 CTX DIRETO - V2)
    # ---------------------------------------------------------

    def build_user_prompt(
        self,
        *,
        ctx: dict,
        action: str,
    ) -> str:

        action = self.normalize_action(action)

        summary = ctx.get("summary") or ""
        events = ctx.get("recent_events") or []
        retrieved = ctx.get("retrieved") or ""
        entities = ctx.get("related_entities") or []
        scene_type = self._normalize_scene(ctx.get("scene_type"))

        instruction = self._get_instruction(scene_type)

        parts = []

        # 🔥 memória longa
        if summary:
            parts.append(f"Resumo da sessão:\n{summary.strip()}")

        # 🔥 eventos recentes
        if events:
            ev = "\n".join(f"- {e}" for e in events[-5:] if e)
            if ev:
                parts.append(f"Eventos recentes:\n{ev}")

        # 🔥 entidades
        if entities:
            unique = list(dict.fromkeys(entities))
            parts.append(
                "Elementos importantes:\n" +
                ", ".join(unique)
            )

        # 🔥 retrieval
        if retrieved:
            parts.append(f"Memória relevante:\n{retrieved.strip()}")

        context_block = "\n\n".join(parts).strip()

        return (
            f"{context_block}\n\n"
            f"Ação do jogador:\n{action}\n\n"
            f"{instruction}"
        )

    # ---------------------------------------------------------
    # STYLE
    # ---------------------------------------------------------

    def _get_style(self, scene_type: str) -> str:

        if scene_type in ("ACTION", "COMBAT"):
            return (
                "ESTILO:\n"
                "- Frases curtas\n"
                "- Ritmo rápido\n"
                "- Foco em ação imediata\n\n"
            )

        if scene_type in ("CHAT", "DIALOGUE"):
            return (
                "ESTILO:\n"
                "- Diálogo natural\n"
                "- Emoções e expressões\n\n"
            )

        if scene_type == "INVESTIGATION":
            return (
                "ESTILO:\n"
                "- Observação detalhada\n"
                "- Ênfase em pistas\n\n"
            )

        return (
            "ESTILO:\n"
            "- Narrativa imersiva\n"
            "- Descrições sensoriais\n\n"
        )

    # ---------------------------------------------------------
    # INSTRUCTION
    # ---------------------------------------------------------

    def _get_instruction(self, scene_type: str) -> str:

        if scene_type in ("ACTION", "COMBAT"):
            return "Descreva a consequência imediata da ação."

        if scene_type in ("CHAT", "DIALOGUE"):
            return "Continue a interação entre personagens."

        if scene_type == "INVESTIGATION":
            return "Revele pistas ou detalhes relevantes."

        return "Continue a narrativa."

    # ---------------------------------------------------------
    # CONFIG
    # ---------------------------------------------------------

    def get_generation_config(self, scene_type: str) -> dict:

        scene_type = self._normalize_scene(scene_type)

        if scene_type in ("ACTION", "COMBAT"):
            return {"temperature": 0.6, "max_tokens": 200}

        if scene_type in ("CHAT", "DIALOGUE"):
            return {"temperature": 0.75, "max_tokens": 300}

        if scene_type == "INVESTIGATION":
            return {"temperature": 0.65, "max_tokens": 350}

        return {"temperature": 0.85, "max_tokens": 500}

    # ---------------------------------------------------------
    # UTILS
    # ---------------------------------------------------------

    def normalize_action(self, action: str) -> str:
        if not action:
            return ""
        return " ".join(str(action).strip().split())

    def _normalize_scene(self, scene_type: str) -> str:
        return (scene_type or "DEFAULT").upper()

    def sanitize_output(self, text: str) -> str:
        if text is None:
            raise ValueError("Output cannot be None")

        lines = [
            line.strip()
            for line in text.strip().splitlines()
            if line.strip()
        ]

        return "\n".join(lines)

    def enforce_length(self, text: str, max_chars: int) -> str:
        if not text:
            return ""

        if len(text) <= max_chars:
            return text

        return text[:max_chars].rsplit(" ", 1)[0]