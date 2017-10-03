from Commands.CmdHelper import *

# play something in voice chat
@disabled_command("Not currently implemented")
def cmd_play(cmd):
    if cmd.server is None:
        SendMessage(cmd.channel, "This command may only be used in a server.")
        return

    voice = cmd.author.voice
    if voice.voice_channel is None:
        SendMessage(cmd.channel, "You need to be in a voice channel.")
        return

    inSameServer = False
    vc = None
    inSameChannel = False

    # find out if we're in the same server/channel as our inviter.
    for voiceClient in link_bot.discordClient.voice_clients:
        if voiceClient.server == voice.voice_channel.server:
            inSameServer = True
            vc = voiceClient
        if voiceClient.channel == voice.voice_channel:
            inSameChannel = True

    # join the voice channel, either by moving from the current one, or by creating a new voice client.
    if not inSameChannel:
        if inSameServer:
            vc.move_to(voice.voice_channel)
        else:
            link_bot.discordClient.join_voice_channel(voice.voice_channel)

    SendMessage(cmd.channel, "Joined.")
