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
        raise Exception("Message not found")
    try:
        index = reactions.index(emoji)
    except:
        raise Exception("Reaction emoji not found")
    role_lookup = r.get(msgid + "-" + str(index))
    if role_lookup is None:
        eprint("ERROR: Role not found in database.")
        raise Exception("Role not found")
    guild = client.get_guild(payload.guild_id)
    return (
        guild.get_member(payload.user_id),
        guild.get_role(int(role_lookup))
    )

@client.event
async def on_raw_reaction_add(payload):
    try:
        (user, role) = roles_process_payload(payload)
        await user.add_roles(role)
    except:
        return

@client.event
async def on_raw_reaction_remove(payload):
    try:
        (user, role) = roles_process_payload(payload)
        await user.remove_roles(role)
    except:
        return

@client.command(pass_context=True)
async def set_roles(ctx, *args):
    num_roles = len(args)
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.channel.send('You must be an administrator of this server to run this command.')
    if num_roles == 0 or num_roles > 10:
        await ctx.channel.send('Please specify (up to 10) role titles for auto-roling.')
    else:
        embedVar = discord.Embed(
            title='Role Selection',
            description='Click the corresponding reaction to assign yourself a role! ' \
                'You can remove an added role by removing your reaction.',
            color=0x006600
        )
        truncated = reactions[:num_roles]
        guild = ctx.guild
        roles = []
        for i in range(num_roles):
            embedVar.add_field(name=args[i], value=truncated[i], inline=True)
            roles.append(await guild.create_role(name=args[i]))
        msg = await ctx.channel.send(embed=embedVar)
        for emoji in truncated:
            await msg.add_reaction(emoji)
        msgid = str(msg.id)
        r.set(msgid, num_roles)
        for i in range(num_roles):
            r.set(msgid + "-" + str(i), roles[i].id)

@client.command(pass_context=True)
async def verify(ctx, *args):
    mention = ctx.message.author.mention
    user = ctx.message.author
    if len(args) < 2:
        await ctx.channel.send('Please specify both your role ' \
            '(`student`/`staff`) and your Andrew ID. For example: ' \
            '`!verify student rxun`')
    elif args[0] == 'student':
        lookup = r.get('student-' + args[1])
        if lookup is None:
            await ctx.channel.send(mention + ', Honk was unable to verify ' \
                'you: either you are not a 15-122 student this semester, your ' \
                'Andrew ID was entered incorrectly, or our roster is outdated ' \
                '(please reach out to Ruiran if this is the case!).')
        elif lookup == -1:
            await ctx.channel.send(mention + ', you have already been verified!')
        else:
            role = discord.utils.get(ctx.guild.roles, name='student')
            await user.add_roles(role)
            r.set('student-' + args[1], user.id)
            await ctx.channel.send(mention + ', you have been successfully ' \
                'verified! Welcome :honk:')
    elif args[0] == 'staff':
        lookup = r.get('staff-' + args[1])
        if lookup is None:
            await ctx.channel.send(mention + ', Honk was unable to verify ' \
                'you: either you are not a 15-122 TA this semester, your ' \
                'Andrew ID was entered incorrectly, or our TA roster on the ' \
                'database is incorrect (please reach out to Ruiran if this ' \
                'is the case!).')
        elif lookup == -1:
            await ctx.channel.send(mention + ', you have already been verified!')
        else:
            role = discord.utils.get(ctx.guild.roles, name='staff')
            await user.add_roles(role)
            r.set('staff-' + args[1], user.id)
            await ctx.channel.send(mention + ', you have been successfully ' \
                'verified! Welcome :honk:')
    else:
        await ctx.channel.send('Please specify a valid role (either `student` ' \
            'or `staff`.')
        
@client.command(pass_context=True)
async def add_student(ctx, *args):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.channel.send('You must be an administrator of this server to run this command.')
    elif len(args) == 0:
        await ctx.channel.send('Please specify one or more students to add to the roster.')
    else:
        for andrewid in args:
            r.set('student-' + andrewid, -1)
        await ctx.channel.send('Successfully added ' + str(len(args)) + ' student(s) to the roster.')

@client.command(pass_context=True)
async def add_staff(ctx, *args):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.channel.send('You must be an administrator of this server to run this command.')
    elif len(args) == 0:
        await ctx.channel.send('Please specify one or more TAs to add to the roster.')
    else:
        for andrewid in args:
            r.set('staff-' + andrewid, -1)
        await ctx.channel.send('Successfully added ' + str(len(args)) + ' TA(s) to the roster.')

@client.command(pass_context=True)
async def remove_student(ctx, *args):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.channel.send('You must be an administrator of this server to run this command.')
    elif len(args) == 0:
        await ctx.channel.send('Please specify one or more students to remove from the roster.')
    else:
        for andrewid in args:
            r.set('student-' + andrewid, -1)
        await ctx.channel.send('Successfully removed ' + str(len(args)) + ' student(s) from the roster.')

@client.command(pass_context=True)
async def remove_staff(ctx, *args):
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.channel.send('You must be an administrator of this server to run this command.')
    elif len(args) == 0:
        await ctx.channel.send('Please specify one or more TAs to remove from the roster.')
    else:
        for andrewid in args:
            r.set('staff-' + andrewid, -1)
        await ctx.channel.send('Successfully removed ' + str(len(args)) + ' TA(s) from the roster.')    

client.remove_command('help')   # override default help command
@client.command(pass_context=True)
async def help(ctx):
    embedVar = discord.Embed(title="HonkBot Help", color=0x006600)
    embedVar.add_field(
        name='`!verify <student/staff> <andrewID>`',
        value='Verifies a user as a student or TA. Example usage: ' \
            '`!verify student rxun`',
        inline=False
    )
    embedVar.add_field(
        name='`!set_roles <role0> <role1> ...`',
        value='Turns the arguments into server roles, enabling users to ' \
            'add the roles to themselves by reacting to a message. (Note ' \
            'that this can only be run by administrators.)',
        inline=False
    )
    embedVar.add_field(
        name='`!add_student <andrewID0> <andrewID1> ...`',
        value='Adds the users with specified Andrew IDs as verifiable ' \
            'students. (Note that this can only be run by administrators.)',
        inline=False
    )
    embedVar.add_field(
        name='`!add_staff <andrewID0> <andrewID1> ...`',
        value='Adds the users with specified Andrew IDs as verifiable ' \
            'TAs. (Note that this can only be run by administrators.)',
        inline=False
    )
    embedVar.add_field(
        name='`!remove_student <andrewID0> <andrewID1> ...`',
        value='Removes the users with specified Andrew IDs from the verifiable ' \
            'student roster. (Note that this can only be run by administrators.)',
        inline=False
    )
    embedVar.add_field(
        name='`!remove_staff <andrewID0> <andrewID1> ...`',
        value='Removes the users with specified Andrew IDs from the verifiable ' \
            'TA roster. (Note that this can only be run by administrators.)',
        inline=False
    )
    embedVar.add_field(
        name='`!help`',
        value='Displays this message.',
        inline=False
    )
    await(ctx.channel.send(embed=embedVar))

client.run(DISCORD_TOKEN)
