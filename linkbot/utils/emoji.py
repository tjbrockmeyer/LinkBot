
checkmark = '✅'
x = '❌'
no_entry = '⛔'
exclamation = '❗'
warning = '⚠'


async def send_success(message):
    await message.add_reaction(emoji=checkmark)