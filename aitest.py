import openai

def load_gpt_key(file_path):
    with open(file_path, 'r') as file:
        return file.readline().strip()

openai.api_key = load_gpt_key("tokens/chatgptkey.txt")

def load_context_from_file(file_path):
    # Load static context prompts from the file (if any)
    messages = []
    with open(file_path, 'r') as file:
        for line in file:
            role, content = line.strip().split(":", 1)
            messages.append({"role": role.lower(), "content": content.strip()})
    return messages

def chat_with_gpt(prompt, recent_messages, max_context_length=5):
    # Add the user prompt to recent messages
    recent_messages.append({"role": "user", "content": prompt})

    # Trim recent messages to keep only the last `max_context_length` exchanges
    recent_messages = recent_messages[-max_context_length:]

    # Send recent_messages only to the model (not context_messages)
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",
        messages=recent_messages
    )

    # Get the response and add it to recent messages
    bot_reply = response.choices[0].message.content.strip()
    recent_messages.append({"role": "assistant", "content": bot_reply})

    # Trim recent_messages again to ensure only the last few exchanges are kept
    recent_messages = recent_messages[-max_context_length:]

    return bot_reply, recent_messages

if __name__ == "__main__":
    # Load context for reference but do not use it in recent messages
    context_file = "prompt.txt"
    context_messages = load_context_from_file(context_file)  # Loaded for reference but unused in conversation
    recent_messages = []  # Initialize with an empty recent_messages list

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            break
        response, recent_messages = chat_with_gpt(user_input, recent_messages)
        print("Chatbot:", response)
