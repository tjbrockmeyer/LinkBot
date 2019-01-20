
class Letter:
    a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z = \
        "🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", \
        "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"
    alphabet = [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z]


class Symbol:
    white_check_mark = "✅"
    x = "❌"
    no_entry = '⛔'
    exclamation = '❗'
    warning = '⚠'
    grey_question = '❔'

    arrow_backward = "◀"
    arrow_forward = "▶"
    arrow_up_small = "🔼"
    arrow_down_small = "🔽"

    heart = "❤"
    information_source = "ℹ"
    crown = "👑"
    calendar = "📆"
    cake = "🍰"
    birthday = "🎂"
    confetti_ball = "🎊"
    congratulations = "㊗"
    beers = "🍻"



async def send_success(message):
    await message.add_reaction(emoji=Symbol.white_check_mark)