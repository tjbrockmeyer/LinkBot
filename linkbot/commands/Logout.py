from linkbot.utils.cmd_utils import *


@command( [], "", [], aliases=['logoff'], show_in_help=False)
@restrict(OWNER_ONLY)
async def logout(cmd: Command):
    await send_success(cmd.message)
    await client.logout()
    await client.close()


@command([], "", [], aliases=['reload', 'reboot'], show_in_help=False)
@restrict(OWNER_ONLY)
async def restart(cmd: Command):
    bot.restart = True
    await logout(cmd)


@command([], "", [], show_in_help=False)
@restrict(OWNER_ONLY)
async def dbg(cmd: Command):
    if cmd.args:
        await xyz()
    else:
        await abc()

async def abc():
    import linkbot.utils.menu as dmm
    import linkbot.utils.emoji as emoji

    page = 0
    last_page = 3
    submenu = False

    def build_embed():
        return discord.Embed(
            title="My fancy menu",
            description="This is a description."
        ).set_footer(
            text="This is a foot. Really.",
            icon_url=client.user.avatar_url
        )

    def build_options():
        options = default_options[:]
        if submenu:
            options.append(go_back_button)
        if page != 0:
            options.append(previous_page_button)
        if page != last_page:
            options.append(next_page_button)
        options.append(exit_button)
        return options

    def page_right(_):
        nonlocal page; page += 1
    def page_left(_):
        nonlocal page; page -= 1

    go_back_button = dmm.Option(emoji.Symbol.arrow_up_small, "Main menu")
    previous_page_button = dmm.Option(emoji.Symbol.arrow_backward, "Previous Page", func=page_left, refresh=True)
    next_page_button = dmm.Option(emoji.Symbol.arrow_forward, "Next Page", func=page_right, refresh=True)
    exit_button = dmm.Option(emoji.Symbol.x, "Exit", close=True)
    default_options = [
        dmm.Option(emoji.Letter.a, "Eyyyyy"),
        dmm.Option(emoji.Letter.b, "Beeeees?"),
    ]

    await dmm.send(bot.owner, dmm.Menu(embed=build_embed, options=build_options))

async def xyz():
    import linkbot.utils.menu as dmm
    import linkbot.utils.emoji as emoji

    user_settings = dmm.Menu()
    server_settings = dmm.Menu()
    main_menu = dmm.Menu()

    back_to_main = dmm.Option(emoji.Symbol.arrow_up_small, "Back to main menu", next_menu=main_menu)
    close_menu = dmm.Option(emoji.Symbol.x, "Close menu", close=True)

    user_settings.embed = discord.Embed(
        title="User Settings",
        description="Now here are some settings!"
    )
    user_settings.options = [
        dmm.Option(emoji.Letter.a, "Toggle notifications"),
        dmm.Option(emoji.Letter.b, "Blahblah"),
        back_to_main, close_menu
    ]

    server_settings.embed = discord.Embed(
        title="Server Settings",
        description="I wish that I had some settings that I could put in here... Oh wait..."
    )
    server_settings.options = [
        dmm.Option(emoji.Letter.a, "gejfoi"),
        dmm.Option(emoji.Letter.b, "Blahblah"),
        dmm.Option(emoji.Letter.c, "less blah"),
        dmm.Option(emoji.Letter.d, "more blahblah"),
        back_to_main, close_menu
    ]

    main_menu.embed = discord.Embed(
        title="Main Menu",
        description="Right now, you're probably\nwondering how this can be so cool."
    )
    main_menu.options = [
        dmm.Option(emoji.Letter.a, "User settings", next_menu=user_settings),
        dmm.Option(emoji.Letter.b, "Server settings", next_menu=server_settings),
        close_menu
    ]

    await dmm.send(bot.owner, main_menu)

