import asyncio
import time
import discord
from Commands.CmdHelper import *


# move all members in a particular voice chat to a different one
def cmd_migrate(cmd: Command):
    logging.info("Command: migrate")

    # On Server check.
    if cmd.server is None:
        SendMessage(cmd.channel, "You can only use this command on a server.")
        return

    # Enough args check.
    if len(cmd.args) < 2:
        cmd.OnSyntaxError('Provide two voice channels as arguments.')
        return

    cmd.args = cmd.argstr.split(',')
    channels = []
    for c in cmd.args:
        channels.append(c.strip())

    channel1 = None
    channel2 = None

    # find the two channels.
    for channel in cmd.server.channels:
        if channel.type == discord.ChannelType.voice:
            if channel.name.lower() == channels[0].lower():
                channel1 = channel
            elif channel.name.lower() == channels[1].lower():
                channel2 = channel
            # once they are both found, break the loop.
            if channel1 is not None and channel2 is not None:
                break

    # Report that the loop did not break.
    else:
        if channel1 is None and channel2 is None:
            cmd.OnSyntaxError("Neither '{}' nor '{}' are channels in this server.".format(*channels))
        elif channel1 is None:
            cmd.OnSyntaxError(channels[0] + " is not a channel in this server.")
        elif channel2 is None:
            cmd.OnSyntaxError(channels[1] + " is not a channel in this server.")
        return

    # move each member from the first channel to the second channel.
    for member in channel.voice_members:
        asyncio.run_coroutine_threadsafe(link_bot.discordClient.move_member(member, channel2), cmd.loop)
    SendMessage(cmd.channel, 'Members in {0} have been migrated to {1}.'.format(channel1.name, channel2.name))
    time.sleep(3)