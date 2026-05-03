"""test_firebase_service.py — Database operation tests."""

import pytest

from services.firebase_service import create_journey, get_journey, update_journey_step


class TestCreateJourney:
    @pytest.mark.asyncio
    async def test_creates_journey_in_memory(self):
        result = await create_journey({"state": "bihar", "election_type": "general"})
        assert "id" in result
        assert result["state"] == "bihar"

    @pytest.mark.asyncio
    async def test_journey_has_timestamp(self):
        result = await create_journey({"state": "texas"})
        assert "created_at" in result


class TestGetJourney:
    @pytest.mark.asyncio
    async def test_get_existing_journey(self):
        created = await create_journey({"state": "florida"})
        result = await get_journey(created["id"])
        assert result is not None
        assert result["state"] == "florida"

    @pytest.mark.asyncio
    async def test_get_nonexistent_journey(self):
        result = await get_journey("nonexistent")
        assert result is None


class TestUpdateStep:
    @pytest.mark.asyncio
    async def test_update_step(self):
        created = await create_journey({"state": "ohio"})
        result = await update_journey_step(created["id"], 2, "completed")
        assert result is not None
        assert result["current_step"] == 2
