from typing import List, Dict


class SessionSummarizer:
    """
    Responsável por transformar eventos narrativos em
    um resumo coerente para o LLM.

    🔥 Domínio puro:
    - não conhece LLM
    - não conhece embeddings
    - não acessa IO
    """

    # ---------------------------------------------------------
    # EXTRAÇÃO
    # ---------------------------------------------------------

    def extract(self, events: List[Dict]) -> str:
        """
        Extrai texto relevante dos eventos.

        Espera estrutura:
        {
            "text": "...",
            "type": "...",
            ...
        }
        """

        if not events:
            return ""

        lines = []

        for e in events:
            text = e.get("text")

            if not text:
                continue

            lines.append(text.strip())

        return "\n".join(lines)

    # ---------------------------------------------------------
    # PROMPT
    # ---------------------------------------------------------

    def build_prompt(self, text: str) -> str:
        """
        Constrói prompt para resumo narrativo.
        """

        return f"""
Você é um narrador experiente de RPG.

Resuma a sessão abaixo de forma clara, envolvente e coesa.

Regras:
- Preserve eventos importantes
- Mantenha ordem cronológica
- Destaque decisões dos jogadores
- Seja conciso (máx. 2-4 parágrafos)

Sessão:
{text}

Resumo:
""".strip()
