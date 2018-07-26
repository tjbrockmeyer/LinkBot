from Commands.CmdHelper import *
from GoogleAPI import GoogleAPIError


@require_args(1)
@command
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

