# utils/standard_response.py

def build_response(data=None, ai_message="", tool_message="", reasoning="", success=True, message=""):
    return {
        "status": success,
        "message": message,
        "response": {
            "AIMessage": ai_message,
            "ToolMessage": tool_message,
            "Reasoning": reasoning,
            "Data": data or {},
        }
    }
