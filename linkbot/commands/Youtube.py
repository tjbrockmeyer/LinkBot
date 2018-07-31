from GoogleAPI import GoogleAPIError
from linkbot.utils.cmd_utils import *


@command(
    ["{c} <query>"],
    "Links the first video result of a YouTube search for query",
    [
        ("{c} the dirtiest of dogs",
         "This will link the first youtube video found in the search results for 'the dirtiest of dogs'.")
    ],
    aliases=['yt']
)
@require_args(1)
async def youtube(cmd: Command):
    # get the search results
    try:
        video_list = bot.googleClient.get_video_search_results(cmd.argstr, 1)
    except GoogleAPIError as e:
        raise DeveloperError(
            cmd, "Google API Error:\n  Message: {}\n  Status: {}\n  From URL: {}".format(e, e.status_code, e.url),
            public_reason="An error occurred. The quota limit may have been reached.")

    # send link to first search result
    if len(video_list) == 0:
        raise CommandError(cmd, "No results were found.")
    await cmd.channel.send(video_list[0].url)

