
import database

database.initialize_database()

conversation_id = database.create_conversation("My first chat")
database.save_message(conversation_id, "user", "Hello!")
database.save_message(conversation_id, "assistant", "Hi! How can I help?")

print("Conversations:")
for conversation in database.get_conversations():
    print(dict(conversation))

print("\nMessages:")
for message in database.get_messages(conversation_id):
    print(dict(message))
