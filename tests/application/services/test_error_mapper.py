import pytest

from rpg_narrative_server.application.services.llm.error_mapper import map_http_error
from rpg_narrative_server.application.services.llm.llm_errors import (
    LLMClientError,
    LLMRetryableError,
)


# ---------------------------------------------------------
# 4xx → CLIENT ERROR
# ---------------------------------------------------------

@pytest.mark.parametrize("status", [400, 401, 403, 404, 422, 499])
def test_4xx_raises_client_error(status):
    with pytest.raises(LLMClientError) as exc:
        map_http_error(status, "client error")

    assert "client error" in str(exc.value)


# ---------------------------------------------------------
# NON-4xx → RETRYABLE
# ---------------------------------------------------------

@pytest.mark.parametrize("status", [200, 201, 300, 500, 502, 503])
def test_non_4xx_raises_retryable_error(status):
    with pytest.raises(LLMRetryableError) as exc:
        map_http_error(status, "retry")

    assert "retry" in str(exc.value)


# ---------------------------------------------------------
# EDGE: 399 vs 400 boundary
# ---------------------------------------------------------

def test_boundary_399_not_client_error():
    with pytest.raises(LLMRetryableError):
        map_http_error(399, "edge")


def test_boundary_400_is_client_error():
    with pytest.raises(LLMClientError):
        map_http_error(400, "edge")


# ---------------------------------------------------------
# MESSAGE PROPAGATION
# ---------------------------------------------------------

def test_message_is_preserved():
    msg = "specific error message"

    with pytest.raises(LLMClientError) as exc:
        map_http_error(400, msg)

    assert str(exc.value) == msg