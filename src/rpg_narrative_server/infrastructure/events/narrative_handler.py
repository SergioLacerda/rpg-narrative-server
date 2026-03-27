# src/rpg_narrative_server/infrastructure/events/narrative_handler.py

import logging
from rpg_narrative_server.domain.events.player_action import PlayerActionEvent


logger = logging.getLogger("rpg_narrative_server.events.narrative")


def register_narrative_handler(event_bus):
    def handler(event: PlayerActionEvent):
        logger.info(
            "[NARRATIVE] campaign=%s user=%s action=%s",
            event.campaign_id,
            event.user_id,
            event.action,
        )

    event_bus.subscribe(PlayerActionEvent, handler)
