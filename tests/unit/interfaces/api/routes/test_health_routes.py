def test_health_endpoint(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint_default(client):

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] in ["ready", "loading"]
