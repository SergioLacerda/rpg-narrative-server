from rpg_narrative_server.bootstrap.container import get_container

# ------------------------------
# USE CASES
# ------------------------------


def get_narrative_usecase():
    return get_container().narrative


def get_roll_dice_usecase():
    return get_container().roll_dice


def get_end_session_usecase():
    return get_container().end_session


# ------------------------------
# SERVICES
# ------------------------------


def get_health_service():
    c = get_container()

    if hasattr(c, "health"):
        return c.health

    # fallback seguro
    class DummyHealth:
        async def is_ready(self):
            return True

    return DummyHealth()


# ------------------------------
# INFRA (somente se necessário)
# ------------------------------


def get_event_bus():
    return get_container().event_bus
