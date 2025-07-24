from fastapi_poe import PoeBot, run
from fastapi_poe.types import QueryRequest, SettingsRequest, SettingsResponse

class SearchBot(PoeBot):
    async def get_response(self, request: QueryRequest):
        # Your search logic here
        last_message = request.query[-1].content
        
        # Simple echo for testing
        yield f"You searched for: {last_message}"
        yield f"\nThis is your custom Poe bot responding!"

    async def get_settings(self, setting: SettingsRequest) -> SettingsResponse:
        return SettingsResponse(
            server_bot_dependencies={"GPT-3.5-Turbo": 1}
        )

if __name__ == "__main__":
    run(SearchBot(), access_key="ly7wO81Hvw7vPfzB8d9B1_9B_Fp5rauCqUmWXbJb-kU")