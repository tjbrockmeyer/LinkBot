
from linkbot.bot import client
import asyncio


class Menu:
    def __init__(self, *, embed=None, options=None):
        """
        Menu for use in a DM with the bot. Use reactions to navigate.
        If functions are used to build the embed/options, the menu can be made dynamic.

        :param embed: A discord.Embed representing this menu's body. Alternatively, a function that returns an embed.
        :param options: A list of Options to choose from. Alternatively, a function that returns a list of options.
        """
        self.embed = embed
        self.options = options


class Option:
    def __init__(self, emoji, text, *, func=None, refresh=False, next_menu=None, close=False):
        """
        :param emoji: Emoji to use for selection and identification.
        :param text: Text to display for this option.
        :param func: Optional function to call if this option is selected.
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


async def send(user, menu):
    """
    Send a menu to a user's DMs.
    :param user:
    :param menu:
    :return:
    """
    embed, emojis, e2o, message = None, [], {}, None
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
        name = "**__Navigation__**"
        value = "\n".join([f"{o.emoji} {o.text}" for o in options])
        if embed.fields and embed.fields[-1].name == name:
            embed.set_field_at(len(embed.fields) - 1, name=name, value=value)
        else:
            embed.add_field(name=name, value=value)

        # Set lookups.
        emojis = [o.emoji for o in options]
        e2o = {o.emoji: o for o in options}

        # Send message and reactions.
        message = await user.send(embed=embed)
        for e in emojis:
            await message.add_reaction(e)

    await set_menu(menu)
    try:
        while True:
            def check(_r, _u):
                return _u.id == user.id and message.id == _r.message.id and _r.emoji in e2o.keys()
            reaction, _ = await client.wait_for('reaction_add', timeout=60, check=check)
            message = reaction.message
            option = e2o[reaction.emoji]
            if option.func:
                if asyncio.iscoroutinefunction(option.func):
                    await option.func(user)
                else:
                    option.func(user)
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
            await message.delete()
