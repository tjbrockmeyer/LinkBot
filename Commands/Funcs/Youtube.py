from Commands.CmdHelper import *

# link the first youtube video found using the provided query
def cmd_youtube(cmd: Command):
    logging.info('Command: youtube')

    # check for missing args
    if len(cmd.args) == 0:
        cmd.OnSyntaxError('You must provide a query to search for.')
        return

    # get the search results
    api_request = link_bot.googleClient.search_for_video(cmd.argstr, 1)

    # check for bad status code
    if api_request.status_code != 200:
        SendErrorMessage("Google API Error: \n" + api_request.url)
        SendMessage(cmd.channel, "An unknown error occurred. The quota limit may have been reached.")
        return

    # send link to first search result
    logging.info(api_request.url)
    if len(api_request.json['items']) == 0:
        SendMessage(cmd.channel, "No results were found.")
    else:
        SendMessage(cmd.channel, "https://youtube.com/watch?v=" + api_request.json['items'][0]['id']['videoId'])
        logging.info("Sent YouTube video link.")

