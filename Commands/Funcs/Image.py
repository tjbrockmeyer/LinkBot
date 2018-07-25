from Commands.CmdHelper import *
from GoogleAPI import GoogleAPIError

# link the first image found using the provided query
def cmd_image(cmd: Command):
    logging.info('Command: image')

    # check for missing args
    if len(cmd.args) == 0:
        cmd.on_syntax_error('You must provide a query to search for.')
        return

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
