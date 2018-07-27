from Commands.CmdHelper import *
from GoogleAPI import GoogleAPIError


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
        bot.bot.send_error_message("Google API Error: " + e.json)
        bot.send_message(cmd.channel, "An error occurred. The quota limit may have been reached.")
        return

    # send link to first search result
    if len(video_list) == 0:
        bot.send_message(cmd.channel, "No results were found.")
    else:
        bot.send_message(cmd.channel, video_list[0].url)
        logging.info("Sent YouTube video link.")

