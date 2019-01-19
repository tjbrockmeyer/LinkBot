from linkbot.utils.cmd_utils import *
import re


_syntax_regex = re.compile(r"(\w+)\s+to\s+(\w+)(?:\s+(exclude|include)\s+((?:\w+)(?:,\s*\w+)*))?")


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
@restrict(SERVER_ONLY | ADMIN_ONLY)
async def move(cmd: Command):
    match = _syntax_regex.match(cmd.argstr)
    if not match:
        raise CommandSyntaxError(cmd, "Arguments must be in the form of 'channel to channel'.")

    channels = []
    for c in [match.group(1), match.group(2)]:
        try:
            chn_id = (int(c))
            if chn_id <= len(cmd.guild.voice_channels):
                channels.append(cmd.guild.voice_channels[chn_id])
            else:
                raise CommandError(cmd, f"Voice channel id `{c}` is out of range.")
        except ValueError:
            chn = c.strip().lower()
            x = [(i, y) for (i, y) in enumerate(cmd.guild.voice_channels) if y.name.lower().startswith(chn)]
            if len(x) > 0:
                channels.append(cmd.guild.voice_channels[x[0][0]])
            else:
                raise CommandError(cmd, f"`{c}` is not a prefix for an existing voice channel in this server.")

    whitelist = match.group(3) == "include"
    names = [n.lower().strip() for n in match.group(4).split(',')] if match.group(3) else ['/*--*/']
    for m in channels[0].members:
        for n in names:
            in_list = m.display_name.lower().startswith(n)
            if in_list and whitelist or not in_list and not whitelist:
                await m.move_to(channels[1])
    await send_success(cmd.message)