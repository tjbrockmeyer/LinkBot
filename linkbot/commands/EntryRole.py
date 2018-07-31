from linkbot.utils.cmd_utils import *


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
    if not cmd.args:
        with db.connect() as (conn, cur):
            cur.execute("SELECT entry_role FROM servers WHERE server_id = %s;", [cmd.guild.id])
            role_id = cur.fetchone()[0]
            if not role_id:
                raise CommandError(cmd, 'There is not an entry level role set for this server.')
        role = discord.utils.get(cmd.guild.roles, id=role_id)
        await cmd.channel.send('Entry level role: `{}`'.format(role))

    elif cmd.args[0] == 'set':
        mentions = cmd.message.role_mentions
        if not mentions:
            raise CommandSyntaxError(cmd, "You must at-mention a role in the server to be the entry level role.")
        role = cmd.message.role_mentions[0]
        with db.connect() as (conn, cur):
            cur.execute("UPDATE servers SET entry_role = %s", [role.id])
            conn.commit()
        await send_success(cmd.message)

    elif cmd.args[0] == 'remove':
        with db.connect() as (conn, cur):
            cur.execute("SELECT entry_role FROM servers WHERE server_id = %s;", [cmd.guild.id])
            role_id = cur.fetchone()[0]
            if not role_id:
                raise CommandError(cmd, "There isn't an entry role to remove.")
            cur.execute("UPDATE servers SET entry_role = NULL")
            conn.commit()
        await send_success(cmd.message)
    else:
        raise CommandSyntaxError(cmd, "Invalid subcommand.")


@on_event('ready')
async def entryrole_check_all():
    with db.connect() as (conn, cur):
        cur.execute("SELECT server_id, entry_role FROM servers WHERE entry_role IS NOT NULL;")
        results = cur.fetchall()
    for (guild_id, role_id) in results:
        guild = client.get_guild(guild_id)
        role = discord.utils.get(guild.roles, id=role_id)
        for member in guild.members:
            if len(member.roles) == 1:
                await member.add_roles(member, role)


@on_event('member_join')
async def entryrole_check_one(member):
    with db.connect() as (conn, cur):
        cur.execute("SELECT entry_role FROM servers WHERE server_id = %s", [member.guild.id])
        result = cur.fetchone()
    if result:
        role = discord.utils.get(member.guild.roles, id=result[0])
        await client.add_roles(member, role)
