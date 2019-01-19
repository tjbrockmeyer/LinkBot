
from linkbot.utils.cmd_utils import *
from linkbot.utils.search import search_channels, resolve_search_results


def get_guild_info_channel(guild: discord.Guild):
    with db.Session() as sess:
        channel_id = sess.get_info_channel(guild.id)
    return guild.get_channel(channel_id) if channel_id else guild.system_channel


@command([], "", [], name='infochan', show_in_help=False, help_subcommand=False)
@restrict(ADMIN_ONLY)
async def info_channel(cmd: Command):
    if not cmd.args:
        with db.Session() as sess:
            channel_id = sess.get_info_channel(cmd.guild.id)
        if channel_id:
            await cmd.channel.send(embed=bot.embed(
                c=discord.Color.blurple(),
                title=f"Info channel for {cmd.guild.name}\n"
                      f"{emoji.Symbol.information_source} #{cmd.guild.get_channel(channel_id).name}"))
        else:
            raise CommandError(cmd, "There is currently no registered information channel.")
    else:
        async def local_set_info_channel(channel):
            with db.Session() as sess:
                sess.set_info_channel(cmd.guild.id, channel.id)
            await send_success(cmd.message)

        results = search_channels(cmd.argstr, cmd.guild, 't')
        await resolve_search_results(results, cmd.argstr, 'channels', cmd.author, cmd.channel, local_set_info_channel)