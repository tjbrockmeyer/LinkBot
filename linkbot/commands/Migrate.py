from linkbot.utils.cmd_utils import *


@command(
    ["{c} <ch>, <ch>"],
    "Moves all members inside voice channel 1 to voice channel 2.",
    [
        ("{c} BK lounge, The Potion Shop", "Moves everyone in the BK Lounge to the Potion Shop."),
        ("{c} bk lounge, the potion shop", "It's not case sensitive, so this would still work with the same effect.")
    ]
)
@restrict(SERVER_ONLY | ADMIN_ONLY)
async def migrate(cmd: Command):
    cmd.args = cmd.argstr.split(',')
    if len(cmd.args) < 2:
        raise CommandSyntaxError(cmd, "You must specify two comma-seperated channels.")
    channels = []
    for c in cmd.args:
        try:
            chn_id = (int(c))
            if chn_id <= len(cmd.guild.voice_channels):
                channels.append(cmd.guild.voice_channels[chn_id])
            else:
                raise CommandError(cmd, "Voice channel id `{}` is out of range.".format(c))
        except ValueError:
            chn = c.strip().lower()
            x = [(i, y) for (i, y) in enumerate(cmd.guild.voice_channels) if y.name.lower().startswith(chn)]
            if len(x) > 0:
                channels.append(cmd.guild.voice_channels[x[0][0]])
            else:
                raise CommandError(cmd, "`{}` is not an existing voice channel in this server.".format(c))

    # move each member from the first channel to the second channel.
    for member in channels[0].members:
        await member.move_to(channels[1])
    await send_success(cmd.message)