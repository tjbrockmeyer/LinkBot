import discord

from linkbot.utils.cmd_utils import *



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
            raise CommandSyntaxError(cmd, helpcmd + ' is not a valid command.')
        await send_help(cmd.channel if here else cmd.author, cmd.command_arg)

    # if "help [here]"
    else:
        await send_help(cmd.channel if here else cmd.author)


def get_help_header():
    return '\n' \
       "Argument syntax:  `<mandatory> [optional]`\n" \
       "Command prefix: '{prefix}'\n" \
       "Use `{help_syntax}` to get more info on a particular command, for example: 'help quote'" \
        .format(prefix=bot.prefix, help_syntax=bot.commands['help'].get_syntax_with_format(bot.prefix))


async def send_help(dest, helpcmd=None):
    if helpcmd:
        cmdInfo = bot.commands[helpcmd]
        embed = bot.embed(title="**__" + cmdInfo.command + "__**",
                          color=discord.Color.dark_green(),
                          description=cmdInfo.description)
        cmdInfo.embed_examples(embed, bot.prefix, cmd_as_code=False)
        await dest.send(embed=embed)
    else:
        embed = bot.embed(title="__General Command Help__",
                          color=discord.Color.dark_green(),
                          description=get_help_header())
        for x in sorted(list(set([y for y in bot.commands.values() if y.show_in_help])), key=lambda z: z.command):
            x.embed_syntax(embed, bot.prefix, mk_down='`', title_mk_down='__', sep='\n', inline=True)
        await dest.send(embed=embed)



