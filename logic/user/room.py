from .__init__ import *


# application user
class Rooms:

    def __init__(self, user: dict, room_content: dict):
        self.user: dict = user
        self.room: dict = room_content
        self.id: str = room_content['id']
        self.room_author: str = self.user['username']

        # user "rooms" database instance
        self.database_file: str = f'system/user/account/{self.user["username"]}/{self.user["username"]}.json'

    def new_room(self):
        if os.path.isfile(self.database_file):
            database = TinyDB(self.database_file).table('rooms')
            # check for room existence
            if database.get(Query().id == self.id):
                return f'Room exists'
            else:
                database.insert(self.room)
                return f'Room generated'

    def delete_room(self):
        if os.path.isfile(self.database_file):
            database = TinyDB(self.database_file).table('rooms')
            # check for room existence
            if database.get(Query().id == self.id):
                database.remove(Query().id == self.id)
                return f'Room deleted'
            else:
                return f'Room does not exist'

    def update_room(self):
        if os.path.isfile(self.database_file):
            database = TinyDB(self.database_file).table('rooms')
            # check for room existence
            if database.get(Query().id == self.id):
                database.remove(Query().id == self.id)
                database.insert(self.room)
                return f'Room updated'
            else:
                return f'Room does not exist'

    def get_rooms(self):
        if os.path.isfile(self.database_file):
            database = TinyDB(self.database_file).table('rooms')
            # check for room existence
            if database.all():
                rooms = database.all()
                return rooms
            else:
                return f'No room exists'
