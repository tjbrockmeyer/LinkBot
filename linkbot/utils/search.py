
import discord
import asyncio
import linkbot.utils.database as db
import linkbot.utils.emoji as emoji
import linkbot.utils.menu as menu
from linkbot.utils.misc import split_message, string_search_top_n
from linkbot.bot import LinkBot, client
from typing import Callable, List, Any, Coroutine, Union


def async_lambda(func):
    def wrapper(*args, **kwargs):
        asyncio.ensure_future(func(*args, **kwargs), loop=client.loop)
    return wrapper


def hasSingleMatch(results):
    print(results)
    return (len(results) == 1 and results[0][1] > 65) or (results[0][1] == 100 and results[1][1] < 100)


async def split_and_send_message(target: discord.abc.Messageable, message: str, maxlength: int=2000):
    for msg in split_message(message, maxlength):
        await target.send(msg)


def search_members(query, guild):
    l = [m.name for m in guild.members]
    l += [m.nick for m in guild.members if m.nick]
    l = string_search_top_n(query, l, n=5)
    if hasSingleMatch(l):
        return [guild.get_member_named(l[0][0])]
    members = [guild.get_member_named(name_ratio[0]) for name_ratio in l]
    seen = set()
    seen_add = seen.add
    return [x for x in members if not (x in seen or seen_add(x))]


def search_channels(query: str, guild: discord.Guild, channel_type: str='tvc') -> List[discord.abc.GuildChannel]:
    """
    Do a fuzzy search in a guild for channels.

    :param query: String to fuzzy search the guild channels for
    :param guild: Guild to search in
    :param channel_type: 't': TextChannel, 'v' VoiceChannel, 'c': Category Channel
    :return: List of up to 5 channels that match the query relatively well
    """
    channel_types = []
    if 't' in channel_type:
        channel_types.append(discord.TextChannel)
    if 'v' in channel_type:
        channel_types.append(discord.VoiceChannel)
    if 'c' in channel_type:
        channel_types.append(discord.CategoryChannel)

    channels = [c for c in guild.channels if type(c) in channel_types]
    l = [m.name for m in channels]
    l = string_search_top_n(query, l, n=5)
    if hasSingleMatch(l):
        for c in channels:
            if c.name == l[0][0]:
                return [c]
    l = [i[0] for i in l]
    channels = [c for c in channels if c.name in l]
    return channels




def search_roles(query: str, guild: discord.Guild) -> List[discord.Role]:
    l = [m.name for m in guild.roles]
    l = string_search_top_n(query, l, n=5)
    if hasSingleMatch(l):
        for c in guild.roles:
            if c.name == l[0][0]:
                return [c]
    l = [i[0] for i in l]
    return [c for c in guild.roles if c.name in l]



async def resolve_search_results(
        results: list, search_query: str, searching_for: str,
        user: discord.abc.User, channel: discord.abc.Messageable, on_resolve: Callable[[Any], Coroutine]):
    """
    Resolve the results of a search to only 1 item by messaging the user that initiated the search with a menu.

    :param results: Results of a search
    :param search_query: Query used for the search
    :param searching_for: What was searched for {members, channels, roles}
    :param user: User that will resolve the ambiguity
    :param channel: Channel to message the user in
    :param on_resolve: Function to call when the ambiguity has been resolved
    """

    if searching_for == 'members':
        formatter = lambda m: f"{m}" + (f" ({m.nick})" if m.nick else '')
    elif searching_for == 'channels':
        formatter = lambda c: c.name
    elif searching_for == 'roles':
        formatter = lambda r: r.name
    else:
        raise ValueError("searching_for must be one of {members, channels, roles}")

    def resolver(v):
        async def wrapper(r, u):
            await on_resolve(v)
        return wrapper

    if len(results) == 1:
        await on_resolve(results[0])
        return

    await menu.send(
        dest=channel,
        only_accept=user,
        menu=menu.Menu(
            embed=LinkBot.embed(
                c=discord.Color.lighter_grey(),
                title=f"By '{search_query}', did you mean...?"))
            .set_options([
                menu.Option(emoji.Letter.alphabet[i], formatter(r), func=resolver(r), close=True)
                for i, r in enumerate(results)] + [menu.Option(emoji.Symbol.x, "Close", close=True)]))


def get_guild_info_channel(guild: discord.Guild):
    with db.Session() as sess:
        channel_id = sess.get_info_channel(guild.id)
    return guild.get_channel(channel_id) if channel_id else guild.system_channel