import openai
from openai import OpenAI

def load_gpt_key(file_path):
    key = ''
    with open(file_path, 'r') as file:
        for line in file:
            key = line
    return key

openai.api_key = load_gpt_key("chatgptkey.txt")

def load_context_from_file(file_path):
    messages = []
    with open(file_path, 'r') as file:
        for line in file:
            role, content = line.strip().split(":", 1)
            messages.append({"role": role.lower(), "content": content.strip()})
    return messages

def chat_with_gpt(prompt, context_messages):

    context_messages.append({"role": "user", "content": prompt})

    response = openai.chat.completions.create(
        model = "gpt-4o-mini-2024-07-18",
        
        messages=context_messages )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    context_file = "prompt.txt"
    context_messages = load_context_from_file(context_file)

    while True:
        user_input = input ("User: ")
        if user_input.lower in ["quit", "exit", "bye"]:
            break
        response = chat_with_gpt(user_input, context_messages)
        print("Chatbot:", response)
