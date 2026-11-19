from fastapi.testclient import TestClient

from app.api.routes import webhook as webhook_route
from app.core.config import settings
from app.modules.messages.services.webhook_service import _extract_message


def test_webhook_rejects_invalid_api_key(
    client: TestClient, monkeypatch
) -> None:
    monkeypatch.setattr(settings, "EVOLUTION_API_KEY", "expected-secret")

    response = client.post(
        "/webhook/whatsapp",
        headers={"apikey": "wrong-secret"},
        json={"event": "messages.upsert", "instance": "careconnect-dev", "data": {}},
    )

    assert response.status_code == 401


def test_webhook_ignores_non_message_events(
    client: TestClient, monkeypatch
) -> None:
    monkeypatch.setattr(settings, "EVOLUTION_API_KEY", "expected-secret")
    task_calls = []
    monkeypatch.setattr(
        webhook_route,
        "process_webhook_bg",
        lambda payload: task_calls.append(payload),
    )

    response = client.post(
        "/webhook/whatsapp",
        headers={"apikey": "expected-secret"},
        json={"event": "connection.update", "instance": "careconnect-dev", "data": {}},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ignored", "reason": "Not a message event"}
    assert task_calls == []


def test_webhook_schedules_valid_message_for_background(
    client: TestClient, monkeypatch
) -> None:
    monkeypatch.setattr(settings, "EVOLUTION_API_KEY", "expected-secret")
    task_calls = []
    monkeypatch.setattr(
        webhook_route,
        "process_webhook_bg",
        lambda payload: task_calls.append(payload),
    )
    payload = {
        "event": "messages.upsert",
        "instance": "careconnect-dev",
        "data": {
            "key": {"remoteJid": "558699999999@s.whatsapp.net", "id": "TEST_MSG_123"},
            "pushName": "João da Silva",
            "message": {"conversation": "Olá"},
        },
    }

    response = client.post(
        "/webhook/whatsapp",
        headers={"apikey": "expected-secret"},
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Webhook received"}
    assert task_calls == [payload]


def test_extract_text_and_audio_message_contents() -> None:
    assert _extract_message({"message": {"conversation": "Olá"}}) == ("text", "Olá")
    assert _extract_message(
        {"message": {"extendedTextMessage": {"text": "Oi"}}}
    ) == ("text", "Oi")
    assert _extract_message({"message": {"audioMessage": {}}}) == ("audio", None)
    assert _extract_message({"message": {"imageMessage": {}}}) == ("unknown", None)
