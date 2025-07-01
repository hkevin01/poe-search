"""Direct tests for Poe.com API connection and conversation retrieval."""

import pytest

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import load_poe_tokens_from_file


@pytest.fixture(scope="module")
def poe_tokens():
    return load_poe_tokens_from_file()

@pytest.fixture(scope="module")
def poe_client(poe_tokens):
    client = PoeAPIClient(token=poe_tokens)
    return client

def test_poe_connection(poe_client):
    """Test that we can connect to Poe.com API and get user info."""
    bots = poe_client.get_bots()
    assert isinstance(bots, dict)
    assert len(bots) > 0


def test_get_conversation_ids(poe_client):
    """Test that we can fetch conversation IDs from Poe.com."""
    conv_ids = poe_client.get_conversation_ids()
    assert isinstance(conv_ids, list)
    assert len(conv_ids) > 0


def test_get_conversation(poe_client):
    """Test that we can fetch a conversation by ID from Poe.com."""
    conv_ids = poe_client.get_conversation_ids()
    first_id = conv_ids[0]
    conversation = poe_client.get_conversation(first_id)
    assert conversation is not None
    assert "messages" in conversation or "id" in conversation
