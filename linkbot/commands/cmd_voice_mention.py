from linkbot.utils.cmd_utils import *
from linkbot.utils.search import search_channels, resolve_search_results


@command(
    ["@ <voice channel>"],
    "@ mention all users in a specific voice channel.",
    [("{c} Pallet Town", "@ mentions all users in the Pallet Town voice channel.")],
    name="@",
    help_subcommand=False)
@restrict(SERVER_ONLY)
@require_args(1)
async def voice_mention(cmd: Command):

    async def set_channel(c):
        nonlocal channel
        channel = c

    channel = None
    results = search_channels(cmd.argstr, cmd.guild, 'v')
    await resolve_search_results(results, cmd.argstr, "channels", cmd.author, cmd.channel, set_channel)
    if channel is None:
        return
    if not channel.members:
        raise CommandError(cmd, f"There were no users found in '{channel.name}'.")
    mention = " ".join(m.mention for m in channel.members)
    await cmd.channel.send(mention, embed=bot.embed(
        c=discord.Color.purple(),
        title=f"Attention, all users in {channel.name}!"))
