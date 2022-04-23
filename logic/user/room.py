from .__init__ import *


# application user
class Rooms:

    def __init__(self, user: dict, room_content: dict):
        self.user: dict = user
        self.room: dict = room_content
        self.id: str = room_content['id']
        self.room_author: str = room_content['author']

        # user "rooms" database instance
        self.database_file: str = f'system/user/account/{self.user["email"]}/{self.user["email"]}.json'

    def new_room(self):
        if os.path.isfile(self.database_file):
            database = TinyDB(self.database_file).table('rooms')
            database.insert(self.room)
            return 'Room generated'

    def delete_room(self):
        self.database.remove(Query().id == self.id)

    def update_room(self):
        pass
