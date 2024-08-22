import discord
import handleresponses

async def send_messages(message, user_message):
    try:
        response = handleresponses.handle_response(user_message)
        await message.reply(response, mention_author=True )
    except Exception as e:
        print(e)

def run_discord_bot():
    TOKEN = 'enter token here'
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return  
        
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} said: '{user_message}' ({channel})")

        if user_message[0] == '?':
            user_message = user_message[1:]
            await send_messages(message, user_message)
        else:
            await send_messages(message, user_message)

    client.run(TOKEN)


