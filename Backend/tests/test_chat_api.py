import pytest
from httpx import AsyncClient, ASGITransport
from Streamlit.main import app


# Testira da se automatski dodaje poruka koja zahtijeva odgovore na hrvatskom jeziku
@pytest.mark.asyncio
async def test_chat_adds_croatian_prompt():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/chat/", json={
            "messages": [{"role": "user", "content": "Hello"}]
        })

        assert response.status_code == 200
        text = response.json()["response"].lower()
        assert any(word in text for word in ["bok", "zdravo", "kako", "si"]), f"Unexpected reply: {text}"


# Testira da se ne ponavlja uputa za hrvatski jezik ako je već uključena u porukama
@pytest.mark.asyncio
async def test_chat_respects_existing_croatian_prompt():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/chat/", json={
            "messages": [{"role": "user", "content": "Od sada odgovaraj isključivo na hrvatskom jeziku."}]
        })

        assert response.status_code == 200
        text = response.json()["response"].lower()
        assert "od sada odgovaraj" not in text  # Should not repeat the language instruction
        assert any(word in text for word in ["razumijem", "pitajte", "hrvatskom"]), f"Unexpected reply: {text}"


# Testira da API vraća grešku 400 ako je lista poruka prazna
@pytest.mark.asyncio
async def test_chat_empty_messages_returns_400():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/chat/", json={"messages": []})
        assert response.status_code == 400
        assert "message list cannot be empty" in response.json()["detail"].lower()


# Testira kako API reagira na neispravan format poruke (npr. nedostaje "content")
@pytest.mark.asyncio
async def test_chat_handles_invalid_format():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/chat/", json={
            "messages": [{"role": "user"}]
        })

        # Trebao bi vratiti grešku zbog Pydantic validacije (400 ili 422)
        assert response.status_code in [400, 422]
