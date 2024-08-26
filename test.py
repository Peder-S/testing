import os
import requests
from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint

class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        API_BASE_URL: str = ""
        pass

    def __init__(self):
        super().__init__()
        self.name = "RT Ticket API Pipeline"
        self.valves = self.Valves(**self.valves.model_dump())
    
    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        # Extract user message content
        user_message = self.get_last_user_message(body.get("messages", []))
        if user_message:
            # Parse the input format "RT#ticket-id username password"
            try:
                _, ticket_id, username, password = user_message.split(" ")
                api_url = f"{self.valves.API_BASE_URL}/{ticket_id}/show"
                
                # Make the API call
                response = requests.get(api_url, auth=(username, password))
                if response.status_code == 200:
                    # Update message content with the API response
                    body["messages"][-1]["content"] = response.text
                else:
                    body["messages"][-1]["content"] = f"Error: {response.status_code} - {response.reason}"
            except Exception as e:
                body["messages"][-1]["content"] = f"Error processing input: {str(e)}"
        return body
