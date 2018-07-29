import asyncio
import time
import discord
from commands.cmd_utils import *


@command(
    ["{c} <ch>, <ch>"],
    "Moves all members inside voice channel 1 to voice channel 2.",
    [
        ("{c} BK lounge, The Potion Shop", "Moves everyone in the BK Lounge to the Potion Shop."),
        ("{c} bk lounge, the potion shop", "It's not case sensitive, so this would still work with the same effect.")
    ]
)
@restrict(SERVER_ONLY | ADMIN_ONLY)
@require_args(2)
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
            raise CommandSyntaxError(cmd, "Neither '{}' nor '{}' are channels in this server.".format(*channels))
        elif channel1 is None:
            raise CommandSyntaxError(cmd, channels[0] + " is not a channel in this server.")
        elif channel2 is None:
            raise CommandSyntaxError(cmd, channels[1] + " is not a channel in this server.")

    # move each member from the first channel to the second channel.
    for member in channel1.voice_members:
        await member.move(channel2)
    await send_success(cmd.message)
    time.sleep(3)