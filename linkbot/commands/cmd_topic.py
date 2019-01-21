
from linkbot.utils.cmd_utils import *


@command(
    [
        '{c} list',
        '{c} create <topic>',
        '{c} delete <topic>',
        '{c} subscribe <topic>',
        '{c} unsubscribe <topic>',
        '{c} subscriptions',
        '{c} @ <topic>'
    ],
    "Create topics that members can subscribe to. Ping the subscribers of a topic when you have something to share.",
    [
        ("{c} list", "Displays all topics that are available on this server."),
        ("{c} create Rocket League", "Creates a topic called Rocket League."),
        ("{c} delete Rocket League", "Deletes a topic called Rocket League."),
        ("{c} subscribe Politics", "Subscribe yourself to the topic of Politics."),
        ("{c} unsubscribe Politics", "Unsubscribe yourself from the Politics topic."),
        ("{c} subscriptions", "List all of your subscriptions for the current guild."),
        ("{c} @ Coding", "Mention all members who are subscribed to the Coding topic.")
    ],
    aliases=['topics']
)
@require_args(1)
@restrict(SERVER_ONLY)
async def topic(cmd: Command):
    subarg = cmd.args[0].lower()
    cmd.shiftargs()
    if subarg == 'list':
        await topic_list(cmd)
    elif subarg in ['create', 'add']:
        await topic_create(cmd)
    elif subarg in ['delete', 'remove']:
        await topic_delete(cmd)
    elif subarg in ['sub', 'subscribe']:
        await topic_subscribe(cmd)
    elif subarg in ['unsub', 'unsubscribe']:
        await topic_unsubscribe(cmd)
    elif subarg in ['subs', 'subscriptions']:
        await topic_subscriptions(cmd)
    elif subarg in ['@', 'ping']:
        await topic_ping(cmd)
    else:
        raise CommandSyntaxError(cmd, f"Unknown sub argument '{subarg}'")


async def topic_list(cmd: Command):
    with db.Session() as sess:
        results = sess.get_guild_topics(cmd.guild.id)
    if not results:
        raise CommandError(cmd, f"No one has created any topics for {cmd.guild.name}.")
    await cmd.channel.send(embed=bot.embed(
        c=discord.Color.teal(),
        title="Topics",
        description="\n".join(f"**{name}**: {count} subs" for name, count in results)))


@require_args(1)
async def topic_create(cmd: Command):
    with db.Session() as sess:
        result = sess.get_topic(cmd.guild.id, cmd.argstr)
        if result:
            raise CommandError(cmd, f"A topic named '{cmd.argstr}' already exists.")
        sess.create_topic(cmd.guild.id, cmd.argstr)
    await send_success(cmd.message)


@restrict(ADMIN_ONLY)
@require_args(1)
async def topic_delete(cmd: Command):
    with db.Session() as sess:
        result = sess.get_topic(cmd.guild.id, cmd.argstr)
        if not result:
            raise CommandError(cmd, f"No topic named '{cmd.argstr}' exists.")
        sess.delete_node_with_id(result[0])
    await send_success(cmd.message)


@require_args(1)
async def topic_subscribe(cmd: Command):
    with db.Session() as sess:
        result = sess.get_topic(cmd.guild.id, cmd.argstr)
        if not result:
            raise CommandError(cmd, f"No topic named '{cmd.argstr}' exists.")
        sess.create_sub_to_topic(cmd.guild.id, cmd.author.id, cmd.argstr)
    await send_success(cmd.message)


@require_args(1)
async def topic_unsubscribe(cmd: Command):
    with db.Session() as sess:
        result = sess.get_topic(cmd.guild.id, cmd.argstr)
        if not result:
            raise CommandError(cmd, f"No topic named '{cmd.argstr}' exists.")
        sess.delete_sub_to_topic(cmd.guild.id, cmd.author.id, cmd.argstr)
    await send_success(cmd.message)


async def topic_subscriptions(cmd: Command):
    with db.Session() as sess:
        results = sess.get_member_subscriptions(cmd.guild.id, cmd.author.id)
    if not results:
        raise CommandError(cmd, "You are not subscribed to any topics.")
    await cmd.channel.send(embed=bot.embed(
        c=discord.Color.teal(),
        title=f"Your Topic Subscriptions for {cmd.guild.name}",
        description="\n".join(results)))


async def topic_ping(cmd: Command):
    with db.Session() as sess:
        results = sess.get_topic_subs(cmd.guild.id, cmd.argstr)
    if not results:
        raise CommandError(cmd, "Either the topic does not exist, or there are no subscribers.")
    await cmd.channel.send(" ".join(cmd.guild.get_member(r).mention for r in results), embed=bot.embed(
        c=discord.Color.teal(),
        title=f"Attention all {cmd.argstr} subscribers!"))
