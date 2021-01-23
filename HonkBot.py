import os
import sys

from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

import redis
REDIS_TOKEN = os.getenv('REDIS_TOKEN')
r = redis.from_url(REDIS_TOKEN)

intents = discord.Intents().all()
client = commands.Bot(command_prefix='!', intents=intents)

role_data = {}
reactions = [
    '\U00000030\U0000FE0F\U000020E3',
    '\U00000031\U0000FE0F\U000020E3',
    '\U00000032\U0000FE0F\U000020E3',
    '\U00000033\U0000FE0F\U000020E3',
    '\U00000034\U0000FE0F\U000020E3',
    '\U00000035\U0000FE0F\U000020E3',
    '\U00000036\U0000FE0F\U000020E3',
    '\U00000037\U0000FE0F\U000020E3',
    '\U00000038\U0000FE0F\U000020E3',
    '\U00000039\U0000FE0F\U000020E3'
]

@client.event
async def on_ready():
    '''
    Logs in and sets status message.
    '''
    print('Logged in as ' + str(client.user.name) + '(' + str(client.user.id) + ')')
    await client.change_presence(activity=discord.Game("run !help for more info"))

def roles_process_payload(payload):
    '''
    Preprocesses payload data into the reacting user and the requested role to
    be added or removed.
    '''
    msgid = str(payload.message_id)
    emoji = str(payload.emoji)
    message_lookup = r.get(msgid)
    if message_lookup is None:
        return
    try:
        index = reactions.index(emoji)
    except:
        return
    role_lookup = r.get(msgid + "-" + str(index))
    if role_lookup is None:
        eprint("ERROR: Role not found in database.")
        return
    guild = client.get_guild(payload.guild_id)
    return (
        guild.get_member(payload.user_id),
        guild.get_role(int(role_lookup))
    )

@client.event
async def on_raw_reaction_add(payload):
    (user, role) = roles_process_payload(payload)
    await user.add_roles(role)

@client.event
async def on_raw_reaction_remove(payload):
    (user, role) = roles_process_payload(payload)
    await user.remove_roles(role)

@client.command(pass_context=True)
async def test(ctx, *args):
    for s in args:
        print("arg: " + s)

@client.command(pass_context=True)
async def set_roles(ctx, *args):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.channel.send('You must be an administrator of this server to run this command.')
    if len(args) == 0 or len(args) > 10:
        await ctx.channel.send('Please specify (up to 10) role titles for auto-roling.')
    else:
        embedVar = discord.Embed(
            title='Role Selection',
            description='Click the corresponding reaction to assign yourself a role! \
                You can remove an added role by removing your reaction.',
            color=0x006600
        )
        truncated = reactions[:len(args)]
        guild = ctx.guild
        roles = []
        for i in range(len(truncated)):
            embedVar.add_field(name=args[i], value=truncated[i], inline=True)
            roles.append(await guild.create_role(name=args[i]))
        msg = await ctx.channel.send(embed=embedVar)
        for emoji in truncated:
            await msg.add_reaction(emoji)
        msgid = str(msg.id)
        r.set(msgid, len(truncated))
        for i in range(len(truncated)):
            r.set(msgid + "-" + str(i), roles[i].id)
        role_data[msg.id] = args


client.remove_command('help')   # override default help command
@client.command(pass_context=True)
async def help(ctx):
    embedVar = discord.Embed(title="HonkBot Help", color=0x006600)
    embedVar.add_field(
        name='!set_roles',
        value='Turns the arguments into server roles, enabling users to \
            add the roles to themselves by reacting to a message. (Note \
            that this can only be run by administrators.)',
        inline=False
    )
    await(ctx.channel.send(embed=embedVar))

client.run(DISCORD_TOKEN)
