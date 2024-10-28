import discord
from discord.ext import commands
import openai
import json
from datetime import datetime
from dateutil import parser

# Load OpenAI API Key
def load_gpt_key(file_path):
    with open(file_path, 'r') as file:
        return file.readline().strip()

openai.api_key = load_gpt_key("tokens/chatgptkey.txt")

# Load Discord Token
def load_token(file_path):
    with open(file_path, 'r') as file:
        return file.readline().strip()

# Load static context from file
def load_context_from_file(file_path):
    messages = []
    with open(file_path, 'r') as file:
        for line in file:
            role, content = line.strip().split(":", 1)
            messages.append({"role": role.lower(), "content": content.strip()})
    return messages

# ChatGPT conversation function
def chat_with_gpt(prompt, recent_messages, static_context, max_context_length=5):
    # Add the user prompt to recent messages
    recent_messages.append({"role": "user", "content": prompt})

    # Trim recent messages to keep only the last `max_context_length` exchanges
    recent_messages = recent_messages[-max_context_length:]

    # Combine static context and recent messages for model input
    messages = static_context + recent_messages

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-2024-07-18",
        messages=messages
    )

    # Get the response and add it to recent messages
    bot_reply = response.choices[0].message.content.strip()
    recent_messages.append({"role": "assistant", "content": bot_reply})

    # Trim recent_messages again to maintain only the last few exchanges
    recent_messages = recent_messages[-max_context_length:]

    return bot_reply, recent_messages

# Run Discord Bot
def run_discord_bot():
    TOKEN = load_token("tokens/discordbottoken.txt")
    
    intents = discord.Intents.default()
    intents.message_content = True
    
    client = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)
    
    # Load static context once at startup
    static_context = load_context_from_file("prompt.txt")

    # Store recent messages for each user
    user_conversations = {}

    @client.event
    async def on_ready():
        print(f'{client.user} is now running')
    
    # Chat command to ask questions
    @client.command(name="ask", 
                    description="chat with the KSU AI chatbot",
                    aliases=["a", "chat"],
                    help="ask questions about KSU AI Club through the chatbot")
    async def ask(ctx, *, user_input:str):
        # Get the user's recent message history
        user_id = str(ctx.author.id)
        if user_id not in user_conversations:
            user_conversations[user_id] = []

        # Retrieve and update recent messages specific to the user
        recent_messages = user_conversations[user_id]
        
        # Get the bot response and update the user's conversation history
        response, recent_messages = chat_with_gpt(user_input, recent_messages, static_context)
        user_conversations[user_id] = recent_messages  # Update the user's conversation history

        # Send response, splitting if too long
        if len(response) > 2000:
            parts = [response[i:i + 1900] for i in range(0, len(response), 1900)]
            for part in parts:
                await ctx.reply(part)
        else:
            await ctx.reply(response)

    client.run(TOKEN)

# Run the bot function
run_discord_bot()
