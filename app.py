
import streamlit as st
import ollama

MODEL = "qwen2.5-coder:3b"

st.set_page_config(
    page_title="Local AI Chatbot",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Local AI Chatbot")
st.caption("Powered by Ollama and Qwen2.5-Coder — runs locally on your machine.")

# Keep conversation history during the current Streamlit session.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear the current conversation.
with st.sidebar:
    st.subheader("Chat settings")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Display previous messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept a new question.
if prompt := st.chat_input("Ask me anything..."):
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

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as error:
                st.error(
                    "Could not connect to Ollama. "
                    "Check that Ollama is running and the model is installed."
                )
                st.caption(f"Technical details: {error}")
                st.session_state.messages.pop()
