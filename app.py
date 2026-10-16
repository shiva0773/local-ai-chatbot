
import streamlit as st
import ollama
import database

MODEL = "qwen2.5-coder:3b"

st.set_page_config(
    page_title="Local AI Chatbot",
    page_icon="🤖",
    layout="centered",
)

database.initialize_database()

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


def start_new_chat():
    conversation_id = database.create_conversation()
    st.session_state.conversation_id = conversation_id
    st.session_state.messages = []


def load_chat(conversation_id):
    st.session_state.conversation_id = conversation_id
    saved_messages = database.get_messages(conversation_id)
    st.session_state.messages = [
        {"role": message["role"], "content": message["content"]}
        for message in saved_messages
    ]


st.title("🤖 Local AI Chatbot")
st.caption("Powered by Ollama and SQLite")

with st.sidebar:
    st.header("Your chats")

    if st.button("➕ New chat", use_container_width=True):
        start_new_chat()
        st.rerun()

    conversations = database.get_conversations()

    for conversation in conversations:
        label = conversation["title"]
        if st.button(
            label,
            key=f"chat_{conversation['id']}",
            use_container_width=True,
        ):
            load_chat(conversation["id"])
            st.rerun()

    st.divider()
    st.caption(f"Model: {MODEL}")

# Display the selected conversation.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask me anything...")

if prompt:
    if st.session_state.conversation_id is None:
        start_new_chat()

    conversation_id = st.session_state.conversation_id

    # Save the user's message.
    database.save_message(conversation_id, "user", prompt)
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = ollama.chat(
                    model=MODEL,
                    messages=st.session_state.messages,
                )

                answer = response["message"]["content"]
                st.markdown(answer)

                database.save_message(
                    conversation_id, "assistant", answer
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

                # Name the conversation using its first question.
                if len(st.session_state.messages) == 2:
                    title = prompt.strip().replace("\n", " ")[:45]
                    with database.get_connection() as connection:
                        connection.execute(
                            "UPDATE conversations SET title = ? WHERE id = ?",
                            (title or "New conversation", conversation_id),
                        )

            except Exception as error:
                st.error(
                    "Could not connect to Ollama. "
                    "Check that Ollama is running and the model is installed."
                )
                st.caption(f"Technical details: {error}")

                # Remove the failed user message from the current UI history.
                st.session_state.messages.pop()
                st.rerun()
