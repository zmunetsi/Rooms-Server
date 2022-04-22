import bcrypt

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
        self.password: str = profile['password']
        self.username = profile['username']
        self.country = profile['country']
        self.race = profile['race']
        self.hobbies = profile['hobbies']
        self.health = profile['health']

        # current work directory
        self.account_directory = f'system/user/account/{self.email}'

    # create new user account
    async def create(self):
        # main current work directory
        root_dir = os.getcwd()
        try:
            with open(f'{self.account_directory}/{self.email}.json'):
                return 'Account exists'
        except FileNotFoundError:
            if not os.path.exists(self.account_directory):
                os.makedirs(f'{self.account_directory}')
                os.chdir(self.account_directory)  # change work directory

                # database
                database = TinyDB(f'{self.email}.json')
                database.table('profile').insert(self.profile)
                # restore work dir to root_dir
                os.chdir(root_dir)
                return 'Account generated'

            # restore work dir to root_dir
            os.chdir(root_dir)

    # update user's account values
    async def update(self):
        pass

    # confirm user's security
    async def authenticate(self):
        file = f'{self.account_directory}/{self.email}.json'

        if os.path.exists(file):
            database = TinyDB(file)

            # passwords
            input_password = self.password.encode('utf-8')
            local_password = database.table('profile').all()[0]['password'].encode('utf-8')

            # compare hashed passwords
            if bcrypt.checkpw(input_password, local_password):
                return 'Authentication successful'
            elif ValueError:
                return 'Authentication failure'

        else:
            return 'Account does not exist'

    # pend account for deactivation
    async def deactivate(self):
        if await self.authenticate() == 'Authentication successful':
            if os.path.exists(self.account_directory):
                shutil.rmtree(self.account_directory)
                return 'Account deactivated'
            else:
                return 'Account does not exist'
        else:
            return 'Authentication failure'
