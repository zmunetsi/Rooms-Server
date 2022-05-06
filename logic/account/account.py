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
        self.profile: dict = profile  # user's full profile
        self.email: str = profile['email']
        self.password: str = profile['password']
        self.username: str = profile['username']

        # current work directory
        self.account_directory: str = f'system/user/account/{self.username}'

    # create new user account
    async def create(self):
        # main current work directory
        root_dir = os.getcwd()
        try:
            with open(f'{self.account_directory}/{self.username}.json'):
                return 'Account exists'
        except FileNotFoundError:
            if not os.path.exists(self.account_directory):
                os.makedirs(self.account_directory)
                os.chdir(self.account_directory)  # change work directory

                # database
                database = TinyDB(f'{self.username}.json')

                # HASH USER PASSWORD
                self.profile['password'] = bcrypt.hashpw(self.profile["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                database.table('profile').insert(self.profile)
                # restore work dir to root_dir
                os.chdir(root_dir)
                return 'Account generated'
            else:
                shutil.rmtree(self.account_directory)
                return 'Account-dir exists but not account-file \"Dir removed!\" signup again'

    # update user's account values
    async def update(self):
        pass

    # confirm user's security
    async def authenticate(self):
        file = f'{self.account_directory}/{self.username}.json'

        if os.path.exists(file):
            database = TinyDB(file)

            # passwords
            input_password = self.password.encode('utf-8')
            local_password: str = database.table('profile').all()[0]['password'].encode('utf-8')

            # compare hashed passwords
            try:
                if bcrypt.checkpw(input_password, local_password):
                    return 'Access granted'
                else:
                    return 'Access denied: incorrect password'
            except ValueError as error:
                return f'Access denied: {error}. \"Password not hashed\"'

        else:
            if os.path.exists(self.account_directory):
                shutil.rmtree(self.account_directory)
                return 'Account-dir exists but not account-file \"Dir removed!\" signup again'
            else:
                return 'Account does not exist'

    # pend account for deactivation
    async def delete(self):
        # confirm user security
        if os.path.exists(self.account_directory):
            # confirm user security
            if 'Access granted' in await self.authenticate():
                shutil.rmtree(self.account_directory)
                return 'Account deactivated'
            else:
                return 'Access denied'
        else:
            return 'Account does not exist'

