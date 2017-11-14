from Commands.CmdHelper import *
import discord


# write a particular help panel to the chat.
def cmd_help(cmd: Command):
    logging.info('Command: help   Sending to {0}.'.format(cmd.author))

    # Prevents Circular dependency.
    from Commands.CommandInfo import CommandInfo

    help_header = '\n' \
       "Argument syntax:  `<mandatory> [optional]`\n" \
       "Command prefix: '{prefix}'\n" \
       "Use `{help_syntax}` to get more info on a particular command, for example: 'help quote'" \
        .format(prefix=link_bot.prefix, help_syntax=cmd.info.GetSyntaxWithFormat())

    here = len(cmd.args) > 0 and cmd.args[0].lower() == "here"

    # get optional arguments. If first arg is 'here', set command arg as arg[1]
    if not here and len(cmd.args) > 0:
        command = cmd.args[0].lower()
    elif here and len(cmd.args) > 1:
        command = cmd.args[1].lower()
    else:
        command = None

    # if "help [here] command"
    if command is not None:

        # Check for bad command.
        if not CommandInfo.IsCommand(command):
            cmd.OnSyntaxError(command + ' is not a valid command.')
            return

        cmdInfo = CommandInfo.GetCommandInfo(command)
        embed = discord.Embed(title="**__" + cmdInfo.command + "__**",
                              color=discord.Color(0x127430),
                              description=cmdInfo.description)
        cmdInfo.EmbedExamples(embed, cmd_as_code=False)
        SendMessage(cmd.author if not here else cmd.channel, embed=embed)

        logging.info('Help sent.')

    # if "help [here]"
    else:
        embed = discord.Embed(title="__General Command Help__",
                              color=discord.Color(0x127430),
                              description=help_header)
        for x in CommandInfo.EnumerateCommands_abc():
            x.EmbedSyntax(embed, mk_down='`', title_mk_down='__', sep='\n', inline=True)
        SendMessage(cmd.author if not here else cmd.channel, embed=embed)

        logging.info("Help sent.")

