from fastapi import Request

from rpg_narrative_server.bootstrap.container import Container


# ------------------------------
# CORE
# ------------------------------
def get_container(request: Request) -> Container:
    return request.app.state.container


# ------------------------------
# USE CASES
# ------------------------------
def get_narrative_usecase(request: Request):
    c = get_container(request)
    return c.narrative


def get_roll_dice_usecase(request: Request):
    c = get_container(request)
    return c.roll_dice


def get_end_session_usecase(request: Request):
    c = get_container(request)
    return c.end_session


# ------------------------------
# SERVICES
# ------------------------------
def get_health_service(request: Request):
    c = getattr(request.app.state, "container", None)

    if c and hasattr(c, "health"):
        return c.health

    class DummyHealth:
        async def is_ready(self):
            return True

    return DummyHealth()


# ------------------------------
# INFRA (somente se necessário)
# ------------------------------
def get_event_bus(request: Request):
    c = get_container(request)
    return c.event_bus
