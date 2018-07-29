from commands.cmd_utils import *


MY_SERVER_ID = 153368514390917120
ENTRY_LEVEL_ROLE_ID = 215608168519172096


@command(
    ['{c} set <@role>', '{c} remove'],
    'Set/remove the role to be used as the entry level role.',
    [
        ('{c} set @Noobs', 'Sets the entry level role for this server to Noobs.'),
        ('{c} remove', 'Removes automatic entry level role setting for this server.')
    ]
)
@restrict(SERVER_ONLY)
@update_database
async def entryrole(cmd: Command):
    if len(cmd.args) == 0:
        if 'entryrole' not in bot.data[cmd.guild.id]:
            raise CommandError(cmd, 'There is not an entry level role set for this server.')

        role = discord.utils.get(cmd.guild.roles, id=bot.data[cmd.guild.id]['entryrole'])
        await cmd.channel.send('Entry level role: `{}`'.format(role))

    elif cmd.args[0] == 'set':
        mentions = cmd.message.role_mentions
        if len(mentions) == 0:
            raise CommandSyntaxError(cmd, "You must at-mention a role in the server to be the entry level role.")
        role = cmd.message.role_mentions[0]
        bot.data[cmd.guild.id]['entryrole'] = role.id
        await send_success(cmd.message)

    elif cmd.args[0] == 'remove':
        if 'entryrole' not in bot.data[cmd.guild.id]:
            raise CommandError(cmd, "There isn't an entry role to remove.")
        del bot.data[cmd.guild.id]['entryrole']
    else:
        raise CommandSyntaxError(cmd, "Invalid subcommand.")


@on_event('ready')
async def entryrole_check_all():
    for guild in client.guilds:
        if guild.id in bot.data and 'entryrole' in bot.data[guild.id]:
            role = _get_entryrole(guild)
            for member in guild.members:
                if len(member.roles) == 1:
                    await member.add_roles(member, role)


@on_event('member_join')
async def entryrole_check_one(member):
    if 'entryrole' in bot.data[member.guild.id]:
        role = _get_entryrole(member.guild)
        await client.add_roles(member, role)


def _get_entryrole(guild):
    return discord.utils.get(guild.roles, id=bot.data[guild.id]['entryrole'])
