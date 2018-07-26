from Commands.CmdHelper import *


MY_SERVER_ID = 153368514390917120
ENTRY_LEVEL_ROLE_ID = 215608168519172096


@command
async def entryrole(cmd):
    pass


@on_event('ready')
async def entryrole_check_all():
    guild = bot.client.get_guild(MY_SERVER_ID)
    role = discord.utils.get(guild.roles, id=ENTRY_LEVEL_ROLE_ID)
    for member in guild.members:
        if len(member.roles) == 1:
            await bot.client.add_roles(member, role)


@on_event('member_join')
async def entryrole_check_one(member):
    if member.server.id is MY_SERVER_ID:  # check for 'is paul's server'
        role = discord.utils.get(member.server.roles, id=ENTRY_LEVEL_ROLE_ID)  # find entry level role
        await bot.client.add_roles(member, role)  # assign it
