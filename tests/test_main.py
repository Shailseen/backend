import json
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_echo_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {"message": "hello", "metadata": {"user": "alice"}}
        res = await ac.post("/echo", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "request_id" in data
        assert data["received"]["message"] == "hello"
        assert data["received"]["metadata"]["user"] == "alice"
