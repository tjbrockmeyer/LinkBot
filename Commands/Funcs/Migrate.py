import asyncio
import time
import discord
from Commands.CmdHelper import *


@restrict(SERVER_ONLY)
@require_args(2)
@command
async def migrate(cmd: Command):
    cmd.args = cmd.argstr.split(',')
    channels = []
    for c in cmd.args:
        channels.append(c.strip())

    channel1 = None
    channel2 = None

    # find the two channels.
    for channel in cmd.guild.channels:
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
            cmd.on_syntax_error("Neither '{}' nor '{}' are channels in this server.".format(*channels))
        elif channel1 is None:
            cmd.on_syntax_error(channels[0] + " is not a channel in this server.")
        elif channel2 is None:
            cmd.on_syntax_error(channels[1] + " is not a channel in this server.")
        return

    # move each member from the first channel to the second channel.
    for member in channel.voice_members:
        await bot.client.move_member(member, channel2)
    bot.send_message(cmd.channel, 'Members in {0} have been migrated to {1}.'.format(channel1.name, channel2.name))
    time.sleep(3)