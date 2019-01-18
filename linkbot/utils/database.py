
import logging
import neo4j
from neobolt.exceptions import AuthError, ServiceUnavailable
from linkbot.utils.ini import Ini
from datetime import date


_driver: neo4j.Driver = None


def startup(config_file: str) -> bool:
    """ Setup the connection string and test the connection. Returns True on successful setup. """

    options = Ini.load(config_file)
    global _driver
    try:
        _driver = neo4j.Driver(
            options.str("database.uri"),
            auth=(options.str("database.username"), options.str("database.password")))
    except KeyError as e:
        logging.error(f"Missing key in {config_file}: {e}")
        return False
    except ServiceUnavailable:
        logging.error("The Neo4j database is currently unavailable")
        return False
    except AuthError:
        logging.error("Invalid login credentials")
        return False
    return True


def shutdown():
    if _driver:
        _driver.close()


class Session:
    def __init__(self):
        self.s = _driver.session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.s.close()

    # MANAGE database calls

    def constraints(self):
        """ Run the configured constraints for the database. """
        self.s.run("CREATE CONSTRAINT ON (u:User) ASSERT u.id IS UNIQUE")
        self.s.run("CREATE CONSTRAINT ON (g:Guild) ASSERT g.id IS UNIQUE")
        self.s.run("CREATE CONSTRAINT ON (q:Quote) ASSERT q.ref IS UNIQUE")
        self.s.run("CREATE INDEX ON :User(birthday)")
        self.s.run("CREATE INDEX ON :Reminder(at)")

    def create_guild(self, g_id):
        """ Create a guild object with the given guild id. """

        self.s.run("MERGE (:Guild {id: {g_id}})", g_id=g_id)

    def delete_guild(self, g_id):
        """ Delete a guild object with the given id. This will delete all connected information. """

        self.s.run(
            "MATCH (g:Guild {id: 1001})--(n)\n"
            "DETACH DELETE g, n", g_id=g_id)

    def sync_members(self, g_id, m_ids):
        """ Members not in the list will be disconnected, and members in the list will be created and/or connected
            with the given guild."""

        self.s.run(
            "MATCH (g:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(u:User)\n" 
            "WHERE not u.id in {m_ids}\n"
            "WITH g, m\n"
            "MATCH (g)-[r]-(m)\n"
            "DELETE r\n"
            "CREATE (m)-[:OLD_MEMBER_OF]->(g)", g_id=g_id, m_ids=m_ids)
        self.create_members(g_id, m_ids)

    def create_members(self, g_id, m_ids):
        """ Create user and member objects from the given list of user ids with links to the given guild. """

        self.s.run(
            "MATCH (u:User)<-[:USER]-(m:Member)-[r:OLD_MEMBER_OF]->(g:Guild {id: {g_id}})\n"
            "WHERE u.id in {m_ids}\n"
            "DELETE r\n"
            "CREATE (m)-[:MEMBER_OF]->(g)", g_id=g_id, m_ids=m_ids)
        self.s.run(
            "MATCH (g:Guild {id: {g_id}})\n"
            "FOREACH (v in {m_ids} |\n"
            "  MERGE (u:User {id: v})\n"
            "  MERGE (u)<-[:USER]-(m:Member)-[:MEMBER_OF]->(g))", g_id=g_id, m_ids=m_ids)

    def delete_member(self, g_id, m_id):
        """ Remove the member status relationship between the given member and the given guild. """

        self.s.run(
            "MATCH (g:Guild {id: {g_id}})<-[r:MEMBER_OF]-(m:Member)-[:USER]->(:User {id: {m_id}})\n"
            "DELETE r\n"
            "CREATE (m)-[:OLD_MEMBER_OF]->(g)", g_id=g_id, m_id=m_id)

    # INFO_CHANNEL database calls

    def set_info_channel(self, g_id, c_id):
        """ Set the info channel of the given guild to the given channel. """

        self.s.run(
            "MATCH (g:Guild {id: {g_id}})\n"
            "SET g.infoChannel = {c_id}", g_id=g_id, c_id=c_id)

    def get_info_channel(self, g_id):
        """ Return the channel id of the designated info channel for the given guild.
            Return the system channel if no channel has been specified. """

        result = self.s.run(
            "MATCH (g:Guild {id: {g_id}})\n"
            "WHERE exists(g.infoChannel)\n"
            "RETURN g.infoChannel", g_id=g_id).single()
        return result[0] if result else None

    # ADMIN database calls

    def get_user_is_admin(self, g_id, m_id):
        """ Return true if the user has an admin relationship to the server, false otherwise. """

        result = self.s.run(
            "MATCH (:Guild {id: {g_id}})<-[:ADMIN_OF]-(:Member)-[:USER]->(u:User {id: {m_id}})\n"
            "RETURN count(u) > 0 as c", g_id=g_id, m_id=m_id).single()
        return result[0]

    def get_guild_admins(self, g_id):
        """ Return a list of user ids for all admins in the given guild. """

        results = self.s.run(
            "MATCH (:Guild {id: {g_id}})<-[:ADMIN_OF]-(:Member)-[:USER]->(u:User)\n"
            "RETURN u.id", g_id=g_id)
        return [x[0] for x in results.records()] if results else []

    def create_admins(self, g_id, m_ids):
        """ Create the admin relationship for members of a given server. """

        self.s.run(
            "MATCH (g:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(u:User)\n"
            "WHERE u.id in {m_ids}\n"
            "MERGE (g)<-[:ADMIN_OF]-(m)", g_id=g_id, m_ids=m_ids)

    def delete_admins(self, g_id, m_ids):
        """ Delete the admin relationship for admins of a given server. """

        self.s.run(
            "MATCH (:Guild {id: {g_id}})<-[r:ADMIN_OF]-(:Member)-[:USER]->(u:User)\n"
            "WHERE u.id in {m_ids}\n"
            "DELETE r", g_id=g_id, m_ids=m_ids)

    # BIRTHDAY database calls

    def get_guild_birthdays(self, g_id):
        """ Return the user ids and birthdays of members in the given guild that have registered birthdays. """

        results = self.s.run(
            "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(u:User)\n"
            "WHERE exists(m.birthday)\n"
            "RETURN u.id, m.birthday", g_id=g_id)
        return [(x[0], x[1].to_native()) for x in results.records()] if results else []

    def set_birthday(self, g_id, m_id, bday):
        """ Set the birthday property for the given member of the given guild. """

        self.s.run(
            "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(:User {id: {m_id}})\n"
            "SET m.birthday = {bday}", g_id=g_id, m_id=m_id, bday=bday)

    def remove_birthday(self, g_id, m_id):
        """ Remove the birthday property for the given member of the given guild. """

        self.s.run(
            "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(:User {id: {m_id}})\n"
            "REMOVE m.birthday", g_id=g_id, m_id=m_id)

    def get_unrecognized_birthdays(self, g_id):
        """ Return a list of user ids for members of the given server that have a birthday today
            and it has not yet been recognized. """

        today = date.today()
        today_y1 = date(1, today.month, today.day)
        results = self.s.run(
            "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member {birthday: {today_y1}})-[:USER]->(u:User)\n"
            "WHERE not exists(m.lastCongrats) OR m.lastCongrats <> {today}\n"
            "RETURN u.id", g_id=g_id, today=today, today_y1=today_y1)
        return [x[0] for x in results.records()] if results else []

    def set_birthday_recognition(self, g_id, m_ids):
        """ Set the birthday congradulation date to today for the given members of the given server. """

        today = date.today()
        self.s.run(
            "MATCH (:Guild {id: {g_id}})<-[:MEMBER_OF]-(m:Member)-[:USER]->(u:User)\n"
            "WHERE u.id in {m_ids}\n"
            "SET m.lastCongrats = {today}", g_id=g_id, m_ids=m_ids, today=today)

    # ENTRY_ROLE database calls

    def get_entry_role(self, g_id):
        """ Return the role id for the assigned entry-role of the given server. Return None if it does not exist. """

        result = self.s.run(
            "MATCH (g:Guild {id: {g_id}})\n"
            "WHERE exists(g.entryRole)\n"
            "RETURN g.entryRole", g_id=g_id).single()
        return result[0] if result else None

    def set_entry_role(self, g_id, r_id):
        """ Set the entry-role for the given guild to the given role. """

        self.s.run(
            "MATCH (g:Guild {id: {g_id}})\n"
            "SET g.entryRole = {r_id}", g_id=g_id, r_id=r_id)

    def remove_entry_role(self, g_id):
        """ Remove the entry-role for the given guild. """

        self.s.run(
            "MATCH (g:Guild {id: {g_id}})\n"
            "REMOVE g.entryRole", g_id=g_id)

    def get_guilds_with_entry_roles(self):
        """ Return a (g_id, r_id) tuple for each guild that has an entry role. """

        results = self.s.run(
            "MATCH (g:Guild)\n"
            "WHERE exists(g.entryRole)\n"
            "RETURN g.id, g.entryRole")
        return results.values() if results else []

    # REMINDER database calls

    def delete_reminders_by_user(self, u_id):
        """ Deletes all reminders that are associated with the given user. """

        self.s.run(
            "MATCH (:User {id: {u_id}})<-[reminding:REMINDING]-(r:Reminder)\n"
            "DELETE reminding, r", u_id=u_id)

    def create_reminder(self, u_id, remind_at, reason):
        """ Create a reminder that is set to remind the given user at the given time for the given reason. """

        self.s.run(
            "MATCH (u:User {id: {u_id}})\n"
            "CREATE (u)<-[:REMINDING]-(:Reminder {at: {at}, reason: {reason}})",
            u_id=u_id, at=remind_at, reason=reason)

    def get_reminders_before(self, dtime):
        """ Return a tuple (ID, u_id, at, reason) for each reminder that will occur before the given datetime. """

        results = self.s.run(
            "MATCH (r:Reminder)-[reminding:REMINDING]->(u:User)\n"
            "WHERE r.at < {dt}\n"
            "RETURN ID(r), u.id, r.at, r.reason", dt=dtime)
        return results.values() if results else []

    def delete_reminders_by_ids(self, obj_ids):
        """ Delete all reminders that have object ids present in the given list. """

        self.s.run(
            "MATCH (r:Reminder)-[reminding:REMINDING]->(:User)\n"
            "WHERE ID(r) in {ids}\n"
            "DELETE r, reminding", ids=obj_ids)


