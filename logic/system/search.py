from .__init__ import *


class Search:
    """
    Search for search_value in table(profile) - (username)
    Search for search_value in table(rooms) - (title, description, tags)
    """
    def __init__(self):
        self.root_dir = os.getcwd()

    # search from whom the user rooms with
    def from_roommates(self, username: str, search_value: str):

        accounts_dir = f"{self.root_dir}/system/user/account"

        # if account exists
        if os.path.exists(accounts_dir):
            try:
                find_roommates_database = TinyDB(f'{accounts_dir}/{username}/{username}.json').table('roommates')
                database_roommates_result = find_roommates_database.all()

                # wait to store roommates matching search_value
                local_roommates_result = []

                # COMPARE SEARCH_VALUE WITH DATABASE_ROOMMATES_RESULT
                for user in database_roommates_result:

                    # roommate's table(rooms)
                    roommate_rooms_database = TinyDB(f'{accounts_dir}/{user["username"]}/{user["username"]}.json').table('rooms')
                    roommate_rooms = roommate_rooms_database.all()

                    # ITERATE ROOMMATES ROOMS AND FIND FOR A MATCH
                    for room in roommate_rooms:
                        if search_value:
                            # split description words to list where " ".
                            keys = room['description'].split(' ')
                            for key in keys:
                                # compare each description word with search_value
                                if search_value == key:
                                    local_roommates_result.append(room)

                # RETURN ALL RESULTS AT THE END OF THE LOOP
                return local_roommates_result

            except FileNotFoundError:
                return 'Account does not exist'

    # search from whom the user follows
    def from_following(self, username: str, search_value: str):
        pass

    # search from all users [server functionality only]
    def from_everywhere(self, search_value: str):
        pass
