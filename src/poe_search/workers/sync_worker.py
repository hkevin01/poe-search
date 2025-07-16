
        # Fetch ALL conversations since Poe was created (use a large days value)
        conversations = client.get_conversation_history(days=3650, limit=10000)