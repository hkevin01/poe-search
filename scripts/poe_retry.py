import asyncio
from poe_api_wrapper import AsyncPoeApi
import os
from dotenv import load_dotenv
import time

load_dotenv()

async def test_poe_different_config():
    try:
        # Try with just p-b token first
        tokens = {
            'p-b': os.getenv('POE_P_B')
        }
        
        # Try with different settings
        client = AsyncPoeApi(
            tokens=tokens,
            auto_proxy=True,  # Try with proxy
            sleep_time=3      # Longer delays
        )
        
        print("Attempting connection with auto_proxy...")
        
        # Try a simple bot first
        message = "Hi"
        response = ""
        
        async for chunk in client.send_message("Assistant", message):
            response += chunk
            print(chunk, end='', flush=True)
        
        print(f"\n✅ Success! Full response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Error with auto_proxy: {e}")
        return False

async def test_without_proxy():
    try:
        tokens = {
            'p-b': os.getenv('POE_P_B'),
            'p-lat': os.getenv('POE_P_LAT')
        }
        
        client = AsyncPoeApi(tokens=tokens, auto_proxy=False)
        print("Attempting connection without proxy...")
        
        response = ""
        async for chunk in client.send_message("GPT-3.5-Turbo", "Hello"):
            response += chunk
            print(chunk, end='', flush=True)
        
        print(f"\n✅ Success without proxy!")
        return True
        
    except Exception as e:
        print(f"❌ Error without proxy: {e}")
        return False

if __name__ == "__main__":
    print("Testing Poe API with different configurations...\n")
    
    # Try method 1
    success = asyncio.run(test_poe_different_config())
    
    if not success:
        print("\nTrying without proxy...")
        time.sleep(2)
        success = asyncio.run(test_without_proxy())
    
    if not success:
        print("\n❌ Both methods failed. Let's try manual browser approach...")