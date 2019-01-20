import discord
from linkbot.utils.cmd_utils import *


_help_header = "Argument syntax:  `<mandatory> [optional]`\n" \
               "Use `help [here] command` to get more info on a particular command, for example: 'help quote'"


@command(
    ['{c} [here] [command]'],
    'Pastes help into chat.',
    [
        ("{c} here", "Writes the help panel to the channel you asked for it in."),
        ("{c} quote", "Gets specific help for the 'quote' command."),
        ("{c} here quote", "Writes that specific help to the channel you asked for it in.")
    ],
    name="help"
)
async def cmd_help(cmd: Command):

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
        await send_help(cmd.channel if here else cmd.author, helpcmd)

    # if "help [here]"
    else:
        await send_help(cmd.channel if here else cmd.author)


async def send_help(dest, helpcmd=None):
    if helpcmd:
        cmd_info = bot.commands[helpcmd]
        embed = bot.embed(discord.Color.green(),
                          title="**__" + cmd_info.command_name + "__**",
                          description=cmd_info.description)
        cmd_info.embed_examples(embed, bot.prefix, cmd_as_code=False)
        await dest.send(embed=embed)
    else:
        embed = bot.embed(discord.Color.green(),
                          title="__General Command Help__",
                          description=_help_header)
        for x in sorted(list(set([y for y in bot.commands.values() if y.show_in_help])), key=lambda z: z.command_name):
            x.embed_syntax(embed, bot.prefix, mk_down='`', title_mk_down='__', sep='\n', inline=False)
        await dest.send(embed=embed)



