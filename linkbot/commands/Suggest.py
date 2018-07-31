from linkbot.utils.cmd_utils import *
from linkbot.utils.misc import send_split_message


@command(
    ["{c} <feature>"],
    "Suggest a feature that you think the bot should have. Your suggestion will be saved in a suggestions file.",
    [
        ("{c} Flying puppies please!", "Leaves a suggestion for flying puppies - politely...")
    ]
)
@require_args(1)
async def suggest(cmd: Command):
    subcmd = cmd.args[0]
    cmd.shiftargs()
    if subcmd == 'add':
        if not cmd.args:
            raise CommandSyntaxError(cmd, "You must specify a suggestion.")
        with db.connect() as (conn, cur):
            cur.execute("INSERT INTO suggestions (suggestion) VALUES (%s);", [cmd.argstr])
            conn.commit()
        await send_success(cmd.message)
    elif subcmd == 'remove':
        await suggest_remove(cmd)
    elif subcmd == 'list':
        with db.connect() as (conn, cur):
            cur.execute("SELECT * FROM suggestions;")
            results = cur.fetchall()
        if not results:
            raise CommandError(cmd, "There are not any suggestions at this time.")
        await send_split_message(cmd.channel, "\n".join([f"**{s_id}:**  {text}" for (s_id, text) in results]))


@restrict(OWNER_ONLY)
@require_args(1)
async def suggest_remove(cmd: Command):
    try:
        s_id = int(cmd.args[0])
    except ValueError:
        raise CommandError(cmd, f"{s_id} is not a valid suggestion id.")
    with db.connect() as (conn, cur):
        cur.execute("DELETE FROM suggestions WHERE id = %s;", [cmd.args[0]])
        conn.commit()
    await send_success(cmd.message)
