import pytest

PAYLOAD = {
    "title": "Computador lento",
    "description": "O arranque demora mais de 10 minutos",
    "category": "hardware",
    "priority": "medium",
    "requester": "Joana",
}

def make_ticket(client, **changes):
    response = client.post("/tickets", json={**PAYLOAD, **changes})
    assert response.status_code == 201, response.text
    return response.json()

def test_create_and_read(client):
    ticket = make_ticket(client)
    assert ticket["status"] == "new"
    assert ticket["id"] == 1
    response = client.get(f"/tickets/{ticket['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == PAYLOAD["title"]

def test_default_priority(client):
    payload = {key: value for key, value in PAYLOAD.items() if key != "priority"}
    assert client.post("/tickets", json=payload).json()["priority"] == "medium"

def test_create_validation(client):
    assert client.post("/tickets", json={**PAYLOAD, "category": "printer"}).status_code == 422
    assert client.post("/tickets", json={**PAYLOAD, "title": "a"}).status_code == 422

def test_list_and_filters(client):
    make_ticket(client, title="Erro na VPN", category="network", priority="critical")
    make_ticket(client, title="Impressora avariada", category="hardware", priority="low")
    assert len(client.get("/tickets").json()) == 2
    assert len(client.get("/tickets?category=network").json()) == 1
    assert len(client.get("/tickets?priority=critical").json()) == 1
    assert len(client.get("/tickets?q=vpn").json()) == 1
    assert len(client.get("/tickets?limit=1&offset=1").json()) == 1

def test_update_and_assignment(client):
    ticket = make_ticket(client)
    response = client.put(f"/tickets/{ticket['id']}", json={"assigned_to": "Carlos", "status": "in_progress"})
    assert response.status_code == 200, response.text
    assert response.json()["assigned_to"] == "Carlos"
    assert response.json()["status"] == "in_progress"
    history = client.get(f"/tickets/{ticket['id']}/history").json()
    assert {h["field"] for h in history} == {"created", "assigned_to", "status"}

def test_invalid_transition(client):
    ticket = make_ticket(client)
    r = client.put(f"/tickets/{ticket['id']}", json={"status": "closed"})
    assert r.status_code == 409
    assert client.get(f"/tickets/{ticket['id']}").json()["status"] == "new"

def test_close_terminal(client):
    ticket = make_ticket(client)
    i = ticket['id']
    assert client.put(f"/tickets/{i}", json={"status": "resolved"}).status_code == 200
    assert client.put(f"/tickets/{i}", json={"status": "closed"}).status_code == 200
    assert client.put(f"/tickets/{i}", json={"status": "new"}).status_code == 409
    assert client.put(f"/tickets/{i}", json={"priority": "high"}).status_code == 409

def test_cancel_is_logical(client):
    ticket = make_ticket(client)
    i = ticket['id']
    assert client.delete(f"/tickets/{i}").json()["status"] == "cancelled"
    assert client.get(f"/tickets/{i}").status_code == 200
    assert client.put(f"/tickets/{i}", json={"status": "in_progress"}).status_code == 409

def test_missing_ticket(client):
    assert client.get("/tickets/999").status_code == 404
    assert client.put("/tickets/999", json={"title": "Outro"}).status_code == 404
    assert client.delete("/tickets/999").status_code == 404
    assert client.get("/tickets/999/history").status_code == 404

def test_stats(client):
    make_ticket(client, priority="critical")
    ticket = make_ticket(client, title="Outro problema")
    client.put(f"/tickets/{ticket['id']}", json={"status": "resolved"})
    stats = client.get("/tickets/stats")
    assert stats.status_code == 200
    assert stats.json()["total"] == 2
    assert stats.json()["open"] == 2
    assert stats.json()["critical"] == 1
    assert stats.json()["resolved"] == 1

def test_no_null_required_field(client):
    ticket = make_ticket(client)
    assert client.put(f"/tickets/{ticket['id']}", json={"title": None}).status_code == 409

def test_assign_and_unassign(client):
    ticket = make_ticket(client)
    id_ = ticket["id"]
    assert client.put(f"/tickets/{id_}", json={"assigned_to": "Sara"}).status_code == 200
    assert client.put(f"/tickets/{id_}", json={"assigned_to": None}).json()["assigned_to"] is None


def test_ui_and_static_assets(client):
    assert client.get("/ui").status_code == 200
    assert "OpsBridge" in client.get("/ui").text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/styles.css").status_code == 200
