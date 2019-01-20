
from linkbot.utils.cmd_utils import *
from linkbot.utils.search import search_channels, resolve_search_results
import re


_syntax_regex = re.compile(r"(?:to)?\s+([\w\s]+)(?:\s+(exclude|include)\s+((?:[\w\s]+)(?:,\s*[\w\s]+)*))?")


@command(
    ["{c} to <voice channel>", "{c} to <chan> (include|exclude) <name>, <name>..."],
    "Move members that are in your current voice channel to the given voice channel.",
    [
        ("{c} to bk lounge", "Moves everyone in your current voice channel to the BK Lounge."),
        ("{c} to bk", "Same as the previous example."),
        ("{c} to bk exclude joe, bob", "Moves everyone except Joe and Bob."),
        ("{c} to bk include joe, bob", "Only moves Joe and Bob - no one else."),
    ],
    aliases=['migrate']
)
@restrict(ADMIN_ONLY)
async def move(cmd: Command):
    match = _syntax_regex.match(cmd.argstr)
    if not match:
        raise CommandSyntaxError(cmd, "Arguments must be in the form of 'channel1 to channel2'.")
    voice = cmd.author.voice
    if not voice or not voice.channel:
        raise CommandPermissionError(cmd, "You cannot use this command unless you are in a voice channel.")

    async def set_channel(c):
        nonlocal channel
        channel = c

    channel = None
    r1 = search_channels(match.group(1), cmd.guild, 'v')
    await resolve_search_results(r1, match.group(1), 'channels', cmd.author, cmd.channel, set_channel)
    if not channel:
        return
    whitelist = match.group(2) == "include"
    names = [n.lower().strip() for n in match.group(3).split(',')] if match.group(2) else ['/*--*/']
    for m in voice.channel.members:
        for n in names:
            in_list = m.display_name.lower().startswith(n)
            if in_list and whitelist or not in_list and not whitelist:
                await m.move_to(channel)
    await send_success(cmd.message)