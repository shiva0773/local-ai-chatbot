
import ollama

MODEL = "qwen2.5-coder:3b"


def chat():
    print("🤖 Local AI Chatbot")
    print("Type 'exit' to quit.\n")

    messages = []

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Chatbot: Goodbye!")
            break

        if not user_input:
            continue

        messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            response = ollama.chat(
                model=MODEL,
                messages=messages
            )

            assistant_reply = response["message"]["content"]

            print(f"\nChatbot: {assistant_reply}\n")

            messages.append({
                "role": "assistant",
                "content": assistant_reply
            })

        except Exception as error:
            print(f"Error communicating with Ollama: {error}")
            messages.pop()


if __name__ == "__main__":
    chat()

