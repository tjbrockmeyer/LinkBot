from Commands.CmdHelper import *
import discord


@command(
    ['{c} [here] [command]'],
    'Pastes help into chat.',
    [
        ("{c} here", "Writes the help panel to the channel you asked for it in."),
        ("{c} quote", "Gets specific help for the 'quote' command."),
        ("{c} here quote", "Writes that specific help to the channel you asked for it in.")
    ]
)
async def help(cmd: Command):
    help_header = '\n' \
       "Argument syntax:  `<mandatory> [optional]`\n" \
       "Command prefix: '{prefix}'\n" \
       "Use `{help_syntax}` to get more info on a particular command, for example: 'help quote'" \
        .format(prefix=bot.prefix, help_syntax=cmd.info.get_syntax_with_format())

    here = len(cmd.args) > 0 and cmd.args[0].lower() == "here"

    # get optional arguments. If first arg is 'here', set command arg as arg[1]
    if not here and len(cmd.args) > 0:
        helpcmd = cmd.args[0].lower()
    elif here and len(cmd.args) > 1:
        helpcmd = cmd.args[1].lower()
    else:
        helpcmd = None

    # if "help [here] command"
    if helpcmd is not None:

        # Check for bad command.
        if helpcmd not in bot.commands:
            cmd.on_syntax_error(helpcmd + ' is not a valid command.')
            return

        cmdInfo = bot.commands[helpcmd]
        embed = discord.Embed(title="**__" + cmdInfo.command + "__**",
                              color=discord.Color(0x127430),
                              description=cmdInfo.description)
        cmdInfo.embed_examples(embed, cmd_as_code=False)
        bot.send_message(cmd.author if not here else cmd.channel, embed=embed)

    # if "help [here]"
    else:
        embed = discord.Embed(title="__General Command Help__",
                              color=discord.Color(0x127430),
                              description=help_header)
        for x in sorted(list(set([y for y in bot.commands.values() if y.show_in_help])), key=lambda z: z.command):
            x.embed_syntax(embed, mk_down='`', title_mk_down='__', sep='\n', inline=True)
        bot.send_message(cmd.author if not here else cmd.channel, embed=embed)

