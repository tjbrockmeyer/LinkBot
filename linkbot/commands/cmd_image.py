from GoogleAPI import GoogleAPIError
from linkbot.utils.cmd_utils import *


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
    if not bot.googleClient:
        raise CommandPermissionError(
            cmd, "A Google API key has not been specified. This command is currently disabled.")
    # get the search results
    try:
        image_list = bot.googleClient.get_image_search_results(cmd.argstr)
    except GoogleAPIError as e:
        raise DeveloperError(
            cmd, "Google API Error: \n  Message: {}\n  Status: {}\n  From URL: {}".format(e, e.status_code, e.url),
            public_reason="An error occurred. The quota limit may have been reached.")

    # send link to first search result
    if not image_list:
        raise CommandError(cmd, "No results were found.")
    img = image_list[0]
    await cmd.channel.send(embed=bot.embed(
            discord.Color.blurple()
        ).set_author(
            name=img.title or "Image", url=img.context_url,
            icon_url="https://cdn4.iconfinder.com/data/icons/new-google-logo-2015/400/new-google-favicon-512.png"
        ).set_image(url=img.url))
