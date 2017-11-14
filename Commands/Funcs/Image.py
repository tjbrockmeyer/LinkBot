from Commands.CmdHelper import *

# link the first image found using the provided query
def cmd_image(cmd: Command):
    logging.info('Command: image')

    # check for missing args
    if len(cmd.args) == 0:
        cmd.OnSyntaxError('You must provide a query to search for.')
        return

    # get the search results
    api_request = link_bot.googleClient.google_image_search(cmd.argstr)

    # check for bad status code
    if api_request.status_code != 200:
        SendErrorMessage("Google API Error: \n" + api_request.url)
        SendMessage(cmd.channel, "An error occurred. The quota limit may have been reached.")
        return

    # send link to first search result
    if 'items' in api_request.json:
        SendMessage(cmd.channel, api_request.json['items'][0]['link'])
    else:
        SendMessage(cmd.channel, "No results were found.")
    logging.info("Sent Google image link.")
