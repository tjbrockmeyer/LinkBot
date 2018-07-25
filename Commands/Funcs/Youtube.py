from Commands.CmdHelper import *
from GoogleAPI import GoogleAPIError

# link the first youtube video found using the provided query
def cmd_youtube(cmd: Command):
    logging.info('Command: youtube')

    # check for missing args
    if len(cmd.args) == 0:
        cmd.on_syntax_error('You must provide a query to search for.')
        return

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

