from linkbot.utils.cmd_utils import *
from linkbot.utils.search import search_roles, resolve_search_results


@command(
    ['{c} set <@role>', '{c} remove'],
    'Set/remove the role to be used as the entry level role.',
    [
        ('{c} set @Noobs', 'Sets the entry level role for this server to Noobs.'),
        ('{c} remove', 'Removes automatic entry level role setting for this server.')
    ]
)
@restrict(SERVER_ONLY)
async def entryrole(cmd: Command):

    async def set_role(r):
        nonlocal role
        role = r

    if not cmd.args:
        with db.Session() as sess:
            r_id = sess.get_entry_role(cmd.guild.id)
        if not r_id:
            raise CommandError(cmd, 'There is not an entry level role set for this server.')
        role = discord.utils.get(cmd.guild.roles, id=r_id)
        await cmd.channel.send(embed=bot.embed(
            c=discord.Color.blurple(),
            title=f"Entry Role for {cmd.guild.name}\n{emoji.Symbol.information_source} {role.name}"))

    elif cmd.args[0] == 'set':
        cmd.shiftargs()
        if not cmd.args:
            raise CommandSyntaxError(cmd, "You must provide a role in the server to become the entry level role.")

        role = None
        roles = search_roles(cmd.argstr, cmd.guild)
        await resolve_search_results(roles, cmd.argstr, 'roles', cmd.author, cmd.channel, set_role)
        if not role:
            return
        with db.Session() as sess:
            sess.set_entry_role(cmd.guild.id, role.id)
        await send_success(cmd.message)

    elif cmd.args[0] == 'remove':
        with db.Session() as sess:
            sess.remove_entry_role(cmd.guild.id)
        await send_success(cmd.message)
    else:
        raise CommandSyntaxError(cmd, "Invalid subcommand.")


@on_event('ready')
async def entryrole_check_all():
    with db.Session() as sess:
        results = sess.get_guilds_with_entry_roles()
    for (guild_id, role_id) in results:
        guild = client.get_guild(guild_id)
        role = discord.utils.get(guild.roles, id=role_id)
        for member in guild.members:
            if len(member.roles) == 1:
                await member.add_roles(role)


@on_event('member_join')
async def entryrole_check_one(member):
    with db.Session() as sess:
        r_id = sess.get_entry_role(member.guild.id)
    if r_id:
        role = discord.utils.get(member.guild.roles, id=r_id)
        await member.add_roles(role)
