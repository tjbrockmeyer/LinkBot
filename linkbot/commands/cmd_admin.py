
from linkbot.utils.cmd_utils import *
from linkbot.utils.misc import english_listing


@command(
    ["{c} list", "{c} add <@user|@role>", "{c} remove <@user|@role>"],
    "List admins, or add/remove them.",
    [
        ("{c} list", "Lists all of the admins for this server."),
        ("{c} add @JoeBlow", "Adds JoeBlow as an admin. This has to be a valid mention!"),
        ("{c} add @TheBigDawgs", "If TheBigDawgs is a role, adds all members of TheBigDawgs as admins."),
        ("{c} add @JoeBlow @TheBigDawgs", "Chain mentions together to add multiple people and/or roles as admins"),
        ("{c} remove @JoeBlow @TheBigDawgs", "Removing admins works the same way.")
    ]
)
@restrict(SERVER_ONLY)
@require_args(1)
async def admin(cmd: Command):
    subcmd = cmd.args[0].lower()
    cmd.shiftargs()
    if subcmd == "list":
        await admin_list(cmd)
    elif subcmd == "add":
        await admin_add(cmd)
    elif subcmd == "remove":
        await admin_remove(cmd)
    else:
        raise CommandSyntaxError(cmd, f'{subcmd} is not a valid subcommand.')


async def admin_list(cmd):
    with db.Session() as sess:
        admin_ids = sess.get_guild_admins(cmd.guild.id)
        admins = [cmd.guild.get_member(x) for x in admin_ids]
    if cmd.guild.owner not in admins:
        admins.append(cmd.guild.owner)
    await cmd.channel.send(embed=bot.embed(
        c=discord.Color.gold(),
        title="Admins",
        description=f"{emoji.Symbol.crown} {english_listing([a.display_name for a in admins])}"))


@restrict(ADMIN_ONLY)
async def admin_add(cmd):
    if not cmd.message.mentions and not cmd.message.role_mentions:
        raise CommandSyntaxError(cmd, "You must @-mention at least one role or user.")

    m_ids = set(m.id for m in cmd.message.mentions) \
        .union(set(m.id for r in cmd.message.role_mentions for m in r.members))
    with db.Session() as sess:
        sess.create_admins(cmd.guild.id, list(m_ids))
    await send_success(cmd.message)


@restrict(ADMIN_ONLY)
async def admin_remove(cmd):
    if len(cmd.message.mentions) == 0 and len(cmd.message.role_mentions) == 0:
        raise CommandSyntaxError(cmd, "You must at-mention at least one role or user.")

    m_ids = set(m.id for m in cmd.message.mentions) \
        .union(set(m.id for r in cmd.message.role_mentions for m in r.members))
    with db.Session() as sess:
        sess.delete_admins(cmd.guild.id, list(m_ids))
    await send_success(cmd.message)
