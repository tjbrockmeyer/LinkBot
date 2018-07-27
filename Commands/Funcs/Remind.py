
from Commands.CmdHelper import *
from datetime import datetime, timedelta
from Main.Funcs import load_json, save_json
from Main.LinkBot import DATA_FOLDER
import re


class Reminder:
    datefmt = '%d%m%Y%H%M%S'
    def __init__(self, target, time, reason):
        self.target = target
        self.time = time
        self.reason = reason

    def to_json(self):
        return {'target': self.target.id, 'time': self.time.strftime(Reminder.datefmt), 'reason': self.reason}

    @staticmethod
    def from_json(data):
        return Reminder(
            bot.client.get_user(data['target']),
            datetime.strptime(data['time'], Reminder.datefmt),
            data['reason'])


REMINDERS_FILE = DATA_FOLDER + 'reminders.json'
_delay_regex = re.compile(r"(?:(\d+)d ?)?(?:(\d+)h ?)?(?:(\d+)m ?)?(?:(\d+)s)?")
reminders = []


@command(
    ['{c} me [of <reason>] in #d#h#m#s', '{c} purge'],
    "Mentions you in a message once the given amount of time has passed.",
    [
        ('{c} at 1d 10m', 'Reminds you via a direct message in 1 days and 10 minutes.'),
        ('{c} me of bedtime in 1h 3s', 'Sends you a reminder in 1 hour, 2 minutes and 3 seconds.'),
        ('{c} purge', 'Removes all reminders that are set for you.')
    ]
)
@require_args(1)
async def remind(cmd: Command):
    if cmd.args[0] == 'purge':
        remove = []
        for (index, r) in enumerate(reminders):
            print(r.target, cmd.author)
            if r.target == cmd.author:
                remove.append(index)
        if len(remove) > 0:
            for r in reversed(remove):
                del reminders[r]
            _save_reminders()
        bot.send_message(cmd.channel, "All of your reminders have been deleted (if there were any).")
        return

    try:
        reason = ''
        if cmd.args[0] == 'me':
            cmd.shiftargs()
        if cmd.args[0] == 'of':
            cmd.shiftargs()
            while True:
                if len(cmd.args) == 0:
                    cmd.on_syntax_error('Tell me when to remind you with `in #d#h#m#s`.')
                    return
                elif cmd.args[0] == 'in' and _delay_regex.match(cmd.argstr[3:].strip()):
                    break
                reason += cmd.args[0] + ' '
                cmd.shiftargs()
            reason = reason[:-1]
        if cmd.args[0] == 'in':
            cmd.shiftargs()
    except IndexError:
        cmd.on_syntax_error('You need to specify a delay.')
        return

    try:
        match = _delay_regex.match(cmd.argstr)
        if match:
            days = match.group(1) or 0
            hours = match.group(2) or 0
            minutes = match.group(3) or 0
            seconds = match.group(4) or 0
            delay = int(seconds) + 60 * int(minutes) + 3600 * int(hours) + 86400 * int(days)
        else:
            cmd.on_syntax_error('Delay specification is not in a valid format.')
            return
    except ValueError:
        cmd.on_syntax_error('Days, hours, minutes and seconds can only be whole numbers.')
        return

    now = datetime.now()
    remind_at_time = now + timedelta(seconds=delay)
    reminder = Reminder(cmd.author, remind_at_time, reason)

    if delay < 61:
        bot.client.loop.create_task(remind_soon(reminder))
    else:
        reminders.append(reminder)
        _save_reminders()

    # Exclude date from notification if the reminder will occur within 24 hours.
    if delay < 86400:
        outstring = "I'll remind you at {}".format(remind_at_time.strftime('%I:%M:%S %p'))
    else:
        outstring = "I'll remind you on {} at {}".format(
            remind_at_time.strftime('%a, %b %-m'), remind_at_time.strftime('%I:%M:%S %p'))

    # Include reason in the notification if it was provided.
    if reason != '':
        outstring += ' about "{}".'.format(reason)
    else:
        outstring += '.'
    bot.send_message(cmd.channel, outstring)


@background_task
async def remind_loop():
    min_time = timedelta(seconds=61)
    while not bot.client.is_closed():
        now = datetime.now()
        remove = []
        for (index, r) in enumerate(reminders):
            if r.time - now < min_time:
                remove.append(index)
                bot.client.loop.create_task(remind_soon(r))
        if len(remove) > 0:
            for r in reversed(remove):
                del reminders[r]
            _save_reminders()
        await asyncio.sleep(60)


@on_event('ready')
async def load_reminders():
    global reminders
    reminders = [Reminder.from_json(x) for x in load_json(REMINDERS_FILE)]


async def remind_soon(reminder):
    delta_time = (reminder.time - datetime.now()).total_seconds()
    await asyncio.sleep(delta_time)
    if reminder.reason == '':
        bot.send_message(reminder.target, 'This is your reminder {}!'.format(reminder.target.name))
    else:
        bot.send_message(reminder.target, 'I\'m reminding you about "{}", {}!'.format(reminder.reason, reminder.target.name))


def _save_reminders():
    save_json(REMINDERS_FILE, [r.to_json() for r in reminders])
