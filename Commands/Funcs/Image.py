from Commands.CmdHelper import *
from GoogleAPI import GoogleAPIError


@command(
    ["{c} <query>"],
    "Links the first image result of a Google Image search for `query`.",
    [
        ("{c} what blind people see", "Links the first result of a google image search for 'what blind people see'.")
    ],
    aliases=['img']
)
@require_args(1)
async def image(cmd: Command):
    # get the search results
    try:
        image_list = bot.googleClient.get_image_search_results(cmd.argstr)
    except GoogleAPIError as e:
        bot.send_error_message("Google API Error: \n" + e.url)
        bot.send_message(cmd.channel, "An error occurred. The quota limit may have been reached.")
        return

    # send link to first search result
    if len(image_list) == 0:
        bot.send_message(cmd.channel, "No results were found.")
    else:
        bot.send_message(cmd.channel, image_list[0].url)
    logging.info("Sent Google image link.")
