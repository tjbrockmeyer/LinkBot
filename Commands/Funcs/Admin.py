from Commands.CmdHelper import *
from functools import reduce


@restrict(SERVER_ONLY)
@require_args(1)
@command
def admin(cmd: Command):
    if cmd.guild.id not in bot.data:
        bot.data[cmd.guild.id] = {}
    if 'admins' not in bot.data[cmd.guild.id]:
        bot.data[cmd.guild.id]['admins'] = []

    subcmd = cmd.args[0].lower()
    cmd.shiftargs()
    if subcmd == "list":
        admin_list(cmd)
    elif subcmd == "add":
        admin_add(cmd)
    elif subcmd == "remove":
        admin_remove(cmd)
    else:
        bot.send_message(cmd.channel, '{} is not a valid argument.'.format(subcmd))


def admin_list(cmd):
    # Check for existing admins
    if len(bot.data[cmd.guild.id]['admins']) == 0:
        bot.send_message(cmd.channel, 'There are no admins on this server.')
        return

    # get the admin names from their IDs, save them to a string, then send it to the channel.
    admins = reduce(lambda x, y: "{}, {}".format(x, y) if y in bot.data[cmd.guild.id]['admins'] else x,
                    cmd.guild.members, "Admins: ")
    bot.send_message(cmd.channel, admins)


@restrict(ADMIN_ONLY)
@updates_database
def admin_add(cmd):
    # Check that the sender is an admin
    if not bot.is_admin(cmd.author):
        bot.send_message(cmd.channel, "You must be an admin to use this command.")
        return

    # the output cmd at the end.
    msg = ''

    # if there is a member mention, add them as an admin.
    for member in cmd.message.mentions:
        if member.id in bot.data[cmd.guild.id]['admins']:
            msg += member.display_name + " is already an admin.\n"
        else:
            bot.data[cmd.guild.id]['admins'].append(member.id)
            msg += "Added " + member.display_name + " as an admin.\n"

    # if there is a role mention, add all members with that role as an admin.
    for role in cmd.message.role_mentions:
        for member in cmd.guild.members:
            if role in member.roles:
                if member.id in bot.data[cmd.guild.id]['admins']:
                    msg += member.display_name + " is already an admin.\n"
                else:
                    bot.data[cmd.guild.id]['admins'].append(member.id)
                    msg += "Added " + member.display_name + " as an admin.\n"
    # output
    bot.save_data()
    bot.send_message(cmd.channel, msg)


@restrict(ADMIN_ONLY)
@updates_database
def admin_remove(cmd):
    # Check that the sender is an admin.
    if not bot.is_admin(cmd.author):
        bot.send_message(cmd.channel, "You must be an admin to use this command.")
        return

    # the output message at the end.
    msg = ''

    # if there is a member mention, add them as an admin.
    for member in cmd.message.mentions:
        if member.id not in bot.data[cmd.guild.id]['admins']:
            msg += member.display_name + " is not an admin.\n"
        else:
            bot.data[cmd.guild.id]['admins'].remove(member.id)
            msg += "Removed " + member.display_name + " from the admin list.\n"

    # if there is a role mention, add all members with that role as an admin.
    for role in cmd.message.role_mentions:
        for member in cmd.guild.members:
            if role in member.roles:
                if member.id not in bot.data[cmd.guild.id]['admins']:
                    msg += member.display_name + " is not an admin.\n"
                else:
                    bot.data[cmd.guild.id]['admins'].remove(member.id)
                    msg += "Removed " + member.display_name + " from the admin list.\n"
    # output
    bot.save_data()
    bot.send_message(cmd.channel, msg)
