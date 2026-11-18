import ollama

from agent.tools import calculator

MODEL = "qwen2.5-coder:3b"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate mathematical expressions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to calculate"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


def run_agent(question):

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful AI agent. "
                    "Use the calculator tool whenever mathematical "
                    "calculation is required."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ],
        tools=TOOLS
    )

    message = response["message"]

    # Debug information
    print("\nDEBUG - Complete Ollama response:")
    print(response)

    print("\nDEBUG - Tool calls:")
    print(message.get("tool_calls"))

    print("\nDEBUG - Message content:")
    print(message.get("content"))

    # Check whether the LLM requested a tool
    if message.get("tool_calls"):

        for tool_call in message["tool_calls"]:

            tool_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            if tool_name == "calculator":

                result = calculator(arguments["expression"])

                return f"Calculator result: {result}"

    return message.get("content", "No response generated.")