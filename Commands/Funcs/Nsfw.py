from Commands.CmdHelper import *
from Main.FileWriting import update_config

# enable/disable nsfw content in google searches
@disabled_command("Not currently implemented.")
def cmd_nsfw(cmd):
    logging.info('Command: nsfw')
    if cmd.server is None:
        SendMessage(cmd.channel, "You can only use this command on a server.")
        return
    elif not IsAdmin(cmd.channel):
        SendMessage(cmd.channel, "You must be an admin to use this command.")
        return

    if cmd.args[0].lower() == 'on':
        link_bot.googleClient.set_safe_search(False)
        SendMessage(cmd.channel, "NSFW is now ON.")
        update_config()
    elif cmd.args[0].lower() == 'off':
        link_bot.googleClient.set_safe_search(True)
        link_bot.discordClient.send_message(cmd.channel, "NSFW is now OFF.")
        update_config()
    elif len(cmd.args) == 0:
        if link_bot.nsfw:
            SendMessage(cmd.channel, "NSFW is ON")
        else:
            SendMessage(cmd.channel, "NSFW is OFF")
    else:
        cmd.OnSyntaxError('Specify on or off.')
        return
    logging.info('NSFW has been set/queried.')
