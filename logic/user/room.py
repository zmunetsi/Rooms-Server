from .__init__ import *


# application user
class Rooms:

    def __init__(self, user: dict, room_content: dict):
        self.user: dict = user
        self.room: dict = room_content
        self.id: str = room_content['id']
        self.room_author: str = room_content['author']

        # user "rooms" database instance
        self.database = TinyDB(f'{self.user["email"]}').table('rooms')

    def new_room(self):
        self.database.insert(self.room)

    def delete_room(self):
        self.database.remove(Query().matches())

    def update_room(self):
        pass
