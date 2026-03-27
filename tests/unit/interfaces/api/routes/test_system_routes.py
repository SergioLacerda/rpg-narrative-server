def test_get_system_config(client):
    response = client.get("/system/config")

    assert response.status_code == 200

    data = response.json()

    assert "environment" in data
    assert "storage" in data
    assert "llm_provider" in data


def test_api_router_mounts(client):
    # sanity check geral do router
    response = client.get("/health")

    assert response.status_code == 200
