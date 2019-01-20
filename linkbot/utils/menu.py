
from linkbot.bot import client
import asyncio
import discord
import linkbot.utils.emoji as emoji
from typing import Union, Callable, List, Coroutine, Optional


class Option:
    def __init__(self,
                 emote: str,
                 text: str="", *,
                 func: Callable[[discord.User, discord.Reaction], Optional[Coroutine]]=None,
                 refresh: bool=False,
                 next_menu: 'Menu'=None,
                 close=False):
        """
        :param emote: Emoji to use for selection and identification.
        :param text: Text to display for this option.
        :param func: Optional function to call if this option is selected. Required positional args: (reaction, user)
        :param refresh: If True, the menu will be rebuilt after selecting this option.
        :param next_menu: A menu to switch to after this option is selected.
        :param close: If True, the call to send() will return after selecting this option.
        """
        self.emoji = emote
        self.text = text
        self.func = func
        self.refresh = refresh
        self.next_menu = next_menu
        self.close = close


class Menu:
    def __init__(self,
                 embed: Union[discord.Embed, Callable[[], discord.Embed]], *,
                 show_navigation: bool=True):
        """
        Menu for use in a DM with the bot. Use reactions to navigate.
        If functions are used to build the embed/options, the menu can be made dynamic.

        :param embed: A discord.Embed representing this menu's body. Alternatively, a function that returns an embed.
        :param show_navigation: Whether to show navigation options as an extra field in the embed or not.
        """
        self.embed = embed
        self.show_navigation = show_navigation

        self.options: Union[Callable[[], List[Option]], List[Option]] = []

    def set_options(self, options: Union[Callable[[], List[Option]], List[Option]]) -> 'Menu':
        """
        Set this menu's options.

        :param options: A list of Options to choose from. Alternatively, a function that returns a list of options.
        :return: self, for operation chaining if necessary.
        """
        self.options = options
        return self


async def send_confirmation(dest: discord.abc.Messageable,
                            embed: discord.Embed, *,
                            timeout: int=30,
                            destroy_on_close: bool=True,
                            only_accept: discord.User=None) -> bool:
    """
    Send a confirmation message to the chat, returning True if 'accept' was clicked, False otherwise.

    :param dest: Destination to send the message to.
    :param embed: Embedded message to display.
    :param timeout: Seconds to wait for an answer before closing.
    :param destroy_on_close: If True, the message will be deleted when the coroutine exits.
    :param only_accept: Specify a user to listen for. If not specified, anyone can submit a response.
    :return: True if confirmed, False otherwise.
    """

    def on_yes(r, u):
        nonlocal ret
        ret = True

    ret = False
    options = [
        Option(emoji.Symbol.white_check_mark, "", func=on_yes, close=True),
        Option(emoji.Symbol.x, "", close=True)
    ]
    menu = Menu(embed, show_navigation=False)\
        .set_options(options)
    await send(dest, menu, timeout=timeout, destroy_on_close=destroy_on_close, only_accept=only_accept)
    return ret


async def send_list(dest: discord.abc.Messageable,
                    items: List[str],
                    build_embed: Callable[[], discord.Embed],
                    list_name: str, *,
                    timeout: int=120,
                    per_page: int=10,
                    only_accept: discord.User=None):
    """
    Send a paginated list to a channel. Browse through the list using the arrow reactions.

    :param dest: Channel to send the message to.
    :param items: Full list of items that will be in the list.
    :param build_embed: Function that can build an embed. The list will be concatenated onto this.
    :param list_name: The title of the list. This will be the embed field's `name`.
    :param timeout: Time to wait before removing interactability.
    :param per_page: Number of items to keep on each page.
    :param only_accept: Specify a user to listen for. If not specified, anyone can submit a response.
    """

    def get_embed():
        e = build_embed()
        e.add_field(name=list_name, value="\n".join(items[page * per_page:min((page + 1) * per_page, len(items))]))
        e.add_field(name="*__Page__*", value=f"__{page + 1} of {last_page}__")
        return e

    def get_options():
        options = []
        if page != 0:
            options.append(prev_page_op)
        if (page + 1) < last_page:
            options.append(next_page_op)
        return options

    def change_page(i):
        nonlocal page
        page += i

    next_page_op = Option(emoji.Symbol.arrow_down_small, "Next page", func=lambda r, u: change_page(1), refresh=True)
    prev_page_op = Option(emoji.Symbol.arrow_up_small, "Previous page", func=lambda r, u: change_page(-1), refresh=True)
    page = 0
    last_page = len(items) // per_page + 1
    menu = Menu(embed=get_embed, show_navigation=False).set_options(get_options)
    await send(dest, menu, timeout=timeout, destroy_on_close=False, only_accept=only_accept)


async def send(dest: discord.abc.Messageable,
               menu: Menu, *,
               timeout: int=60,
               destroy_on_close=True,
               only_accept: discord.User=None):
    """
    Send a menu to the specified destination. Options are represented with emoji and can be chosen with reactions.
    The menu will last until the timeout time has been reached.

    :param dest: Channel to send the menu to.
    :param menu: Menu to send.
    :param timeout: Seconds until the menu will automatically close. Pass `None` for no timeout.
    :param destroy_on_close: When the menu closes, if true, the message is deleted, else, the options are removed.
    :param only_accept: Specify a user to listen for. If not specified, anyone can submit a response.
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
            reaction, user = await client.wait_for('reaction_add', timeout=timeout, check=check)
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
            if destroy_on_close:
                await message.delete()
            else:
                for e in emojis:
                    await message.remove_reaction(e, client.user)
