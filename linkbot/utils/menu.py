
from linkbot.bot import client
import asyncio
import discord
import linkbot.utils.emoji as emoji


class Menu:
    def __init__(self, embed, options=None, *, timeout=60, show_navigation=True, destroy_on_close=True):
        """
        Menu for use in a DM with the bot. Use reactions to navigate.
        If functions are used to build the embed/options, the menu can be made dynamic.

        :param embed: A discord.Embed representing this menu's body. Alternatively, a function that returns an embed.
        :param options: A list of Options to choose from. Alternatively, a function that returns a list of options.
        :param timeout: How long in seconds until the menu automatically closes.
        :param show_navigation: Whether to show navigation options as an extra field in the embed or not.
        :param destroy_on_close: Whether the menu should delete on close, or if it should just delete its reactions.
        """
        self.embed = embed
        self.options = options
        self.timeout = timeout
        self.show_navigation = show_navigation
        self.destroy_on_close = destroy_on_close


class Option:
    def __init__(self, emoji, text, *, func=None, refresh=False, next_menu=None, close=False):
        """
        :param emoji: Emoji to use for selection and identification.
        :param text: Text to display for this option.
        :param func: Optional function to call if this option is selected. Required positional args: (reaction, user)
        :param refresh: If True, the menu will be rebuilt after selecting this option.
        :param next_menu: A menu to switch to after this option is selected.
        :param close: If True, the call to send() will return after selecting this option.
        """
        self.emoji = emoji
        self.text = text
        self.func = func
        self.refresh = refresh
        self.next_menu = next_menu
        self.close = close


async def send_confirmation(dest, embed, *, timeout=30, destroy_on_close=True, only_accept=None):

    def on_yes(r, u):
        nonlocal ret
        ret = True

    ret = False
    options = [
        Option(emoji.Symbol.white_check_mark, "", func=on_yes, close=True),
        Option(emoji.Symbol.x, "", close=True)
    ]
    menu = Menu(embed, options=options, timeout=timeout, show_navigation=False, destroy_on_close=destroy_on_close)
    await send(dest, menu, only_accept=only_accept)
    return ret


async def send_list(dest, items, build_embed, list_name, *, timeout=120, per_page=10, only_accept=None):

    def get_embed():
        e = build_embed()
        e.add_field(name=list_name, value="\n".join(items[page * per_page:min((page + 1) * per_page, len(items))]))
        return e

    def get_options():
        options = []
        if page != 0:
            options.append(prev_page_op)
        if (page + 1) * per_page < len(items):
            options.append(next_page_op)
        return options

    def change_page(i):
        nonlocal page
        page += i

    next_page_op = Option(emoji.Symbol.arrow_down_small, "Next page", func=lambda r, u: change_page(1), refresh=True)
    prev_page_op = Option(emoji.Symbol.arrow_up_small, "Previous page", func=lambda r, u: change_page(-1), refresh=True)
    page = 0
    menu = Menu(embed=get_embed, options=get_options, timeout=timeout, show_navigation=False, destroy_on_close=False)
    await send(dest, menu, only_accept=only_accept)


async def send(dest, menu, *, only_accept=None):
    """
    Send a menu to the specified destination.
    If only_accept is specified, only reactions from that user will be accepted as menu input.
    """
    async def set_menu(m):
        nonlocal embed, emojis, e2o, message, menu
        menu = m
        if message:
            await message.delete()

        # Get menu embedded content.
        if callable(menu.embed):
            embed = menu.embed()
        else:
            embed = menu.embed

        # Get menu option content.
        if callable(menu.options):
            options = menu.options()
        else:
            options = menu.options

        # Set the navigation field.
        if menu.show_navigation:
            name = "Options"
            value = "\n".join([f"{o.emoji} {o.text}" for o in options])
            if embed.fields and embed.fields[-1].name == name:
                embed.set_field_at(len(embed.fields) - 1, name=name, value=value)
            else:
                embed.add_field(name=name, value=value)

        # Set lookups.
        emojis = [o.emoji for o in options]
        e2o = {o.emoji: o for o in options}

        # Send message and reactions.
        message = await dest.send(embed=embed)
        for _e in emojis:
            await message.add_reaction(_e)

    embed, emojis, e2o, message = None, [], {}, None
    await set_menu(menu)
    try:
        while True:
            def check(_r, _u):
                return not _u.bot and message.id == _r.message.id and _r.emoji in e2o.keys() and \
                       (not only_accept or _u.id == only_accept.id)
            reaction, user = await client.wait_for('reaction_add', timeout=menu.timeout, check=check)
            message = reaction.message
            option = e2o[reaction.emoji]
            if option.func:
                if asyncio.iscoroutinefunction(option.func):
                    await option.func(reaction, user)
                else:
                    option.func(reaction, user)
            if option.close:
                break
            if option.next_menu:
                await set_menu(option.next_menu)
            if option.refresh:
                await set_menu(menu)

    except asyncio.TimeoutError:
        pass
    finally:
        message = await message.channel.get_message(message.id)
        if message:
            if menu.destroy_on_close:
                await message.delete()
            else:
                for e in emojis:
                    await message.remove_reaction(e, client.user)
