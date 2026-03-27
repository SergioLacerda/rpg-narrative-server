def test_narrative_event_success(client):
    payload = {"action": "look around", "user_id": "user1"}

    response = client.post("/campaign/test/event", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "response" in data


def test_narrative_event_validation_error(client):
    payload = {"action": "", "user_id": "user1"}  # inválido

    response = client.post("/campaign/test/event", json=payload)

    assert response.status_code == 422
