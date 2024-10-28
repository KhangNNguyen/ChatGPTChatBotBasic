import discord
from discord.ext import commands
from typing import Final, List
from util.member import *
from aitest import *
import datetime
from dateutil import parser
import json

def load_token(file_path):
    with open(file_path, 'r') as file:
        return file.readline().strip()

def load_context_from_file(file_path):
    messages = []
    with open(file_path, 'r') as file:
        for line in file:
            role, content = line.strip().split(":", 1)
            messages.append({"role": role.lower(), "content": content.strip()})
    return messages

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

def run_discord_bot():
    TOKEN = load_token("tokens/discordbottoken.txt")
    
    intents = discord.Intents.default()
    intents.message_content = True
    
    client = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

    user_conversations = {}

    @client.event
    async def on_ready():
        print(f'{client.user} is now running')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return  
        
        await client.process_commands(message)
    
    # ==============Profile Creation Commands============== #
    @client.command(name="create", 
                    description="creates a user profile",
                    aliases=["c", "cr"], 
                    help="creates a user profile")
    async def create(ctx):
        user_json = open("users.json", "r")
        users = json.load(user_json)
        
        if ctx.author.display_name.lower() in users.keys():
            await ctx.send(f"Student Profile: **{ctx.author.display_name}** has already been created!")
        else:
            member = Member(ctx.author.id, 
                            ctx.author.display_name, 
                            ctx.author.avatar, 
                            ctx.author.joined_at,
                            ctx.author.color)
            
            users[member.name.lower()] = member.json_format()
            user_json = open("users.json", "w")
            json.dump(users, user_json, indent=3)
            user_json.close()
            
            await ctx.send(f"Student Profile: **{member.name}** has been created!")
    
    @client.command(name="profile", 
                    description="returns the user's profile",
                    aliases=["p"],
                    help="returns the user's profile or show the profile of another user")
    async def profile(ctx, member:str=None):
        user_json = open("users.json", "r")
        users = json.load(user_json)
        try:
            if member is None:
                member_details = users[ctx.author.display_name.lower()]
            else:    
                member_details = users[member.lower()]

            member_details["id"] = int(member_details["id"])
            member_details["join_date"] = parser.parse(member_details["join_date"])
            member_details["profile_color"] = discord.Colour.from_str(member_details["profile_color"])
            
            member = Member(**member_details)
            
            profile_embed = discord.Embed(
                color=member.profile_color,
                title="Profile",
                description=f"""
    >>> 📖 **Bio**: {member.bio}
    🗓️ **Join Date**: {member.join_date.strftime("%m/%d/%Y")}
    **LinkedIn**: {member.linkedin}
                """)

            profile_embed.set_author(name=member.name, icon_url=member.avatar)       
            await ctx.send(embed=profile_embed)
        
        except:
            await ctx.send("Use `!c` or `!create` to create your profile!")
    
    @client.command(name="set", 
                    description="sets the user's profile",
                    aliases=["s"],
                    help="sets the user's profile")
    async def set(ctx, profile_tag: str, *, info:str):
        with open("users.json", "r") as user_json:
            users = json.load(user_json)
        
        member_details = users[ctx.author.display_name.lower()]
        profile_tag_change = ""
        
        if profile_tag.lower() in ("biography", "bio", "b"):
            profile_tag_change = "Bio"
            member_details["bio"] = info
        elif profile_tag.lower() in ("linkedin", "link", "l"):
            profile_tag_change = "LinkedIn"
            member_details["linkedin"] = info
    
        with open("users.json", "w") as user_json:
            json.dump(users, user_json, indent=3)
        
        await ctx.send(f"Your profile **{profile_tag_change}** has been changed!")
    
    # ==============Information Commands============== #
    @client.command(name="owllife", 
                    description="gives the link to the owllife website",
                    aliases=["owl"],
                    help="gives the link to the owllife website")
    async def owllife(ctx):
        await ctx.reply("https://owllife.kennesaw.edu/organization/ai_club")
    
    @client.command(name="events", 
                    description="returns the next upcoming event for ksu ai club",
                    aliases=["e", "event"],
                    help="returns information relating the the next upcoming events for ksu ai club")
    async def events(ctx):
        scheduled_events = ctx.author.guild.scheduled_events
        
        upcoming_event = scheduled_events[0]
        
        event_embed = discord.Embed(
            color=discord.Color.dark_green(),
            title=upcoming_event.name,
            description=upcoming_event.description,
        )
        
        event_embed.add_field(name="Start Time", 
                              value=upcoming_event.start_time.strftime("%m/%d/%Y %H:%M:%S"), 
                              inline=False)
        
        event_embed.add_field(name="End Time",
                              value=upcoming_event.end_time.strftime("%m/%d/%Y %H:%M:%S"), 
                              inline=False)
        
        event_embed.add_field(name="Location", 
                              value=upcoming_event.location, 
                              inline=False)
            
        await ctx.send(embed=event_embed)
        
    # ==============Bot Chat Commands============== #
    @client.command(name="ask", 
                    description="chat with the ksu ai chatbot",
                    aliases=["a", "chat"],
                    help="ask questions about ksu ai club through the ksu ai chatbot")
    async def ask(ctx, *, user_input:str):
        context_file = "prompt.txt"
        context_message = load_context_from_file(context_file)
        
        # Get the user's recent message history
        user_id = str(ctx.author.id)
        if user_id not in user_conversations:
            user_conversations[user_id] = []

        # Retrieve and update recent messages specific to the user
        recent_messages = user_conversations[user_id]
        
        # Get the bot response and update the user's conversation history
        response, recent_messages = chat_with_gpt(user_input, recent_messages, context_message)
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
