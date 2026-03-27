from rpg_narrative_server.domain.events import DiceRolledEvent


def register_dice_handler(event_bus, memory_service):
    def handler(event: DiceRolledEvent):
        memory_service.store({"type": "dice_roll", "result": event.result})

    event_bus.subscribe(DiceRolledEvent, handler)
