import discord
from discord.ext import commands
# import handleresponses
from typing import Final, List

from util.member import *
from aitest import *

import datetime
from dateutil import parser
import re
import json

from rss import RSSparser

# async def send_messages(message, user_message):
#     try:
#         response = handleresponses.handle_response(user_message)
#         for x in response:
#             await message.reply(x, mention_author=True)
#     except Exception as e:
#         print(e)
def converted_from_json_to_details():
    pass


def load_token(file_path):
    token = ''
    with open(file_path, 'r') as file:
        for line in file:
            token = line
    return token

def run_discord_bot():
    TOKEN = load_token("tokens/discordbottoken.txt")
    
    intents = discord.Intents.default()
    intents.message_content = True
    
    client = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

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

        # print(f"{username} said: '{user_message}' ({channel})")
        
        await client.process_commands(message)

        # if user_message[0] == '?':
        #     user_message = user_message[1:]
        #     await send_messages(message, user_message)
        # else:
        #     await send_messages(message, user_message)
    
    
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
                    description="returns the user's profile",
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
            user_json.close()
        
        await ctx.send(f"Your profile **{profile_tag_change}** has been changed!")
    
    
    # ==============Information Commands============== #
    @client.command(name="owllife", 
                    description="gives the link to the owllife website",
                    aliases=["owl"],
                    help="gives the link to the owllife website")

    # this is bad practice but whatever
    async def owllife(ctx, *, user_input:str):
        r = RSSparser()
        r.scrape()
        events = ""
        r.to_string(events)
        context_file = "prompt.txt"
        context_message = load_context_from_file(context_file) + events + "\Provided above is a list of future events scraped from KSU's OwlLife club page. Answer whatever the user asks about these events. Use cases are things like 'what are some events that match my interest in x and y', and then provide 5 or so events that match 5 or so events that match 5 or so events that match 5 or so events that match 5 or so events that match the date, name of the event, and the link. If they didn't ask about upcoming events, tell them that they should submit queries about KSU events using !events and nothing else. format outputs using discord embeds"
        
        response = chat_with_gpt(user_input, context_message)
        if len(response) > 2000:
            out = [(response[i:i+1900]) for i in range (0,len(response), 1900)]
            for part in out:
                await ctx.reply(part)
            #return ("The response is greater than 2000 characters (discord limit) please revise your prompt to limit the response to under 2000 characters. :nerd: ")
        else:
            await ctx.reply(response)


        
    
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
        
        response = chat_with_gpt(user_input, context_message)
        if len(response) > 2000:
            out = [(response[i:i+1900]) for i in range (0,len(response), 1900)]
            for part in out:
                await ctx.reply(part)
            #return ("The response is greater than 2000 characters (discord limit) please revise your prompt to limit the response to under 2000 characters. :nerd: ")
        else:
            await ctx.reply(response)

    client.run(TOKEN)


