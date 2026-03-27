class ContextFormatter:
    def format(self, ctx: dict, scene_type: str = "DEFAULT") -> str:
        parts = []

        summary = ctx.get("summary")
        events = ctx.get("recent_events")
        retrieved = ctx.get("retrieved")
        entities = ctx.get("related_entities")

        # -----------------------------
        # memória longa
        # -----------------------------
        if summary:
            parts.append(f"Resumo da sessão:\n{summary.strip()}")

        # -----------------------------
        # memória recente
        # -----------------------------
        if events:
            events_text = "\n".join(f"- {e}" for e in events[-5:] if e)
            if events_text:
                parts.append(f"Eventos recentes:\n{events_text}")

        # -----------------------------
        # entidades
        # -----------------------------
        if entities:
            parts.append("Entidades relevantes:\n" + ", ".join(dict.fromkeys(entities)))

        # -----------------------------
        # retrieval
        # -----------------------------
        if retrieved:
            parts.append(f"Memória relevante:\n{retrieved.strip()}")

        return "\n\n".join(parts)
