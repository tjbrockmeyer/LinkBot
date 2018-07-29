from commands.cmd_utils import *
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
        raise DeveloperError(
            cmd, "Google API Error: \n  Message: {}\n  Status: {}\n  From URL: {}".format(e, e.status_code, e.url),
            public_reason="An error occurred. The quota limit may have been reached.")

    # send link to first search result
    if len(image_list) == 0:
        raise CommandError(cmd, "No results were found.")
    await cmd.channel.send(image_list[0].url)
