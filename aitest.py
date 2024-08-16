import openai
from openai import OpenAI

openai.api_key = 'Enter your own Open AI API Key here'

def chat_with_gpt(prompt):
    response = openai.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    while True:
        user_input = input ("User: ")
        if user_input.lower in ["quit", "exit", "bye"]:
            break
        response = chat_with_gpt(user_input)
        print("Chatbot:", response)
