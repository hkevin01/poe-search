import asyncio
from poe_api_wrapper import AsyncPoeApi
import os
from dotenv import load_dotenv

load_dotenv()

async def test_poe_wrapper():
    try:
        # Get tokens from .env
        tokens = {
            'p-b': os.getenv('POE_P_B'),
            'p-lat': os.getenv('POE_P_LAT')
        }
        
        client = AsyncPoeApi(tokens=tokens)
        
        # Test message
        async for chunk in client.send_message("Assistant", "Hello! Testing connection."):
            print(chunk, end='', flush=True)
        print("\n✅ Success!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_poe_wrapper())