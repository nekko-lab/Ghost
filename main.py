import discord
from discord import app_commands
import config
import logging
import data
from discord.ext import tasks

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = False
intents.reactions = True
intents.dm_reactions = False
intents.voice_states = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def check_role(guild, role_name):
    for role in guild.roles:
        if role.name == role_name:
            return role
    return None


async def create_role(guild):
    role = await guild.create_role(name=config.ROLE_NAME)
    data.set_role_id(guild.id, role.id)
    return role


async def add_role(guild, member):
    if data.check_member_role(guild.id, member.id):
        return
    
    role_id = data.get_role_id(guild.id)
    if role_id is None:
        await create_role()
        role_id = data.get_role_id(guild.id)

    role = guild.get_role(role_id)
    await member.add_roles(role)
    data.add_member_role(guild.id, member.id)
    print(member.display_name, "add")


async def remove_role(guild, member):
    if not data.check_member_role(guild.id, member.id):
        return
    
    role_id = data.get_role_id(guild.id)
    if role_id is None:
        await create_role()
        role_id = data.get_role_id(guild.id)

    role = guild.get_role(role_id)
    await member.remove_roles(role)
    data.remove_member_role(guild.id, member.id)
    print(member.display_name, "remove")
    

@client.event
async def on_guild_join(guild):
    role = check_role(guild, config.ROLE_NAME)
    if role is None:
        role = await create_role(guild)
    data.new_guild(guild.id, role.id)
    print('join new server, create role')
    async for member in guild.fetch_members(limit=None):
        if not member.bot:
            data.new_member(guild.id, member.id)


@client.event
async def on_ready():
    await tree.sync()
    check_active.start()
    print("Bot is ready.")


async def update(guild, member):
    if not data.check_guild(guild.id):
        await on_guild_join(guild)
    
    if not data.check_member(guild.id, member.id):
        data.new_member(guild.id, member.id)

    data.update_member(guild.id, member.id)
    await remove_role(guild, member)

@client.event
async def on_message(message):
    print(message.author.id)
    if message.author.bot:
        return
    await update(message.guild, message.author)

    
@client.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return
    await update(client.get_guild(payload.guild_id), payload.member)


@client.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return    
    await update(member.guild, member)


@client.event
async def on_member_join(member):
    if member.bot:
        return
    
    if not data.check_guild(member.guild.id):
        await on_guild_join(member.guild)
        
    if not data.check_member(member.guild.id, member.id):
        data.new_member(member.guild.id, member.id)



@tasks.loop(seconds=config.INTERVAL_SEC)
async def check_active():
    print("loop")
    for guild in client.guilds:
        if not data.check_guild(guild.id):
            await on_guild_join(guild)

        for member in guild.members:
            if member.bot:
                continue

            if not data.check_member(guild.id, member.id):
                data.new_member(guild.id, member.id)

            if data.check_active(guild.id, member.id):
                await remove_role(guild, member)
            else:
                await add_role(guild, member)

client.run(config.TOKEN, log_handler=handler, log_level=logging.DEBUG)