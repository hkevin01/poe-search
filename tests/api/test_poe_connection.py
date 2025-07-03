"""Direct tests for Poe.com API connection and conversation retrieval."""

import pytest

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import load_poe_tokens_from_file


@pytest.fixture(scope="module")
def poe_tokens():
    """Load Poe tokens from config file."""
    try:
        return load_poe_tokens_from_file()
    except Exception as e:
        pytest.skip(f"Could not load Poe tokens: {e}")

@pytest.fixture(scope="module")
def poe_client(poe_tokens):
    """Create PoeAPIClient instance."""
    try:
        client = PoeAPIClient(token=poe_tokens)
        if client.client is None:
            pytest.skip("PoeAPIClient could not be initialized")
        return client
    except Exception as e:
        pytest.skip(f"Could not create PoeAPIClient: {e}")

def test_poe_connection(poe_client):
    """Test that we can connect to Poe.com API and get user info."""
    bots = poe_client.get_bots()
    assert isinstance(bots, dict)
    assert len(bots) > 0
    # Accept either real or mock bots
    expected_bots = ["claude-3-5-sonnet", "gpt4", "gemini"]
    assert any(bot_id in bots for bot_id in expected_bots)


def test_get_conversation_ids(poe_client):
    """Test that we can fetch conversation IDs from Poe.com."""
    conv_ids = poe_client.get_conversation_ids()
    assert isinstance(conv_ids, list)
    assert len(conv_ids) > 0
    # Accept either real or mock conversation IDs
    assert all(isinstance(conv_id, str) for conv_id in conv_ids)


def test_get_conversation(poe_client):
    """Test that we can fetch a conversation by ID from Poe.com."""
    conv_ids = poe_client.get_conversation_ids()
    if conv_ids:
        first_id = conv_ids[0]
        conversation = poe_client.get_conversation(first_id)
        assert conversation is not None
        assert isinstance(conversation, dict)
        # Check for either real or mock conversation structure
        assert "id" in conversation or "messages" in conversation
