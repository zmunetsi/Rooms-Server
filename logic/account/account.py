import os.path
import shutil

from .__init__ import *


# user account directory manipulation
class RoomAccount:
    """
    Manipulate user account directory.

    * create - Create new user directory.
    * update - Update user directory to new data.
    * authenticate - Confirm if user account exists -> false | true.
    * remove - Remove/Delete user account directory permanently.
    """

    def __init__(self, profile: dict):
        self.profile = profile  # user's full profile
        self.firstname = profile['firstname']
        self.lastname = profile['lastname']
        self.birth = profile['birth']
        self.gender = profile['gender']
        self.email = profile['email']
        self.password = profile['password']
        self.username = profile['username']
        self.country = profile['country']
        self.race = profile['race']
        self.hobbies = profile['hobbies']
        self.health = profile['health']

        # current work directory
        self.dir = f'system/user/account/{self.email}'

    async def create(self):
        # main current work directory
        root_dir = os.getcwd()
        try:
            with open(f'{self.dir}/{self.email}.json'):
                return 'Account exists'
        except FileNotFoundError:
            if not os.path.exists(self.dir):
                os.makedirs(f'{self.dir}')
                os.chdir(self.dir)  # change work directory

                # database
                database = TinyDB(f'{self.email}.json')
                database.table('profile').insert(self.profile)
                return 'Account generated'

            # restore work dir to root_dir
            os.chdir(root_dir)

    async def update(self):
        print('update...')

    async def authenticate(self):
        database = TinyDB(f'{self.email}.json')

    async def deactivate(self):
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
            return 'Account deactivated'
        else:
            return 'Account does not exist'
