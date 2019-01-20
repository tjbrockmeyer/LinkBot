
from linkbot.utils.cmd_utils import *
from linkbot.utils.search import search_channels, resolve_search_results
import re


_syntax_regex = re.compile(r"([\w\s]+)\s+to\s+([\w\s]+)(?:\s+(exclude|include)\s+((?:[\w\s]+)(?:,\s*[\w\s]+)*))?")


@command(
    ["{c} <chan1> to <chan2>", "<c1> to <c2> (include|exclude) <name>, <name>..."],
    "Move members that are inside voice channel 1 to voice channel 2.",
    [
        ("{c} pallet town to bk lounge", "Moves everyone in Pallet Town to the BK Lounge."),
        ("{c} pall to bk", "Same as the previous example."),
        ("{c} pall to bk exclude joe, bob", "Moves everyone except Joe and Bob."),
        ("{c} pall to bk include joe, bob", "Only moves Joe and Bob - no one else."),
    ],
    aliases=['migrate']
)
@restrict(ADMIN_ONLY)
async def move(cmd: Command):
    match = _syntax_regex.match(cmd.argstr)
    if not match:
        raise CommandSyntaxError(cmd, "Arguments must be in the form of 'channel1 to channel2'.")

    g1, g2 = match.group(1), match.group(2)
    r1 = search_channels(g1, cmd.guild, 'v')
    r2 = search_channels(g2, cmd.guild, 'v')
    c1, c2 = None, None

    async def resolve1(channel):
        nonlocal c1
        c1 = channel

    async def resolve2(channel):
        nonlocal c2
        c2 = channel

    await resolve_search_results(r1, g1, 'channels', cmd.author, cmd.channel, resolve1)
    if not c1:
        return
    await resolve_search_results(r2, g2, 'channels', cmd.author, cmd.channel, resolve2)
    if not c2:
        return

    whitelist = match.group(3) == "include"
    names = [n.lower().strip() for n in match.group(4).split(',')] if match.group(3) else ['/*--*/']
    for m in c1.members:
        for n in names:
            in_list = m.display_name.lower().startswith(n)
            if in_list and whitelist or not in_list and not whitelist:
                await m.move_to(c2)
    await send_success(cmd.message)