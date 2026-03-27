def test_roll_dice(client):
    response = client.get("/utils/roll?expression=1d6")

    assert response.status_code == 200

    data = response.json()

    assert data["expression"] == "1d6"
    assert "result" in data
