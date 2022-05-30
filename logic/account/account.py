from .__init__ import *


# user account directory manipulation
class RoomAccount:
    """
    Manipulate user account directory.

    * create - Create new user directory.
    * update - Update user directory to new data.
    * authenticate - Confirm if user account exists -> false | true.
    * deactivate - Pend user-account for deactivation after number of days.
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
            with open(f'{self.account_directory}/{self.username}.db'):
                return account_exists_true
        except FileNotFoundError:
            if not os.path.exists(self.account_directory):
                os.makedirs(self.account_directory)
                os.chdir(self.account_directory)  # change work directory

                # sqlite database
                database = sqlite3.connect(f'{self.username}.db')
                cursor = database.cursor()
                # create profile table
                cursor.execute("""
                CREATE TABLE profile (data json)
                """)

                # HASH USER PASSWORD
                self.profile['password'] = bcrypt.hashpw(self.profile["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                # store in database
                cursor.execute("insert into profile values (?)", [json.dumps(self.profile)])
                database.commit()

                # restore work dir to root_dir
                os.chdir(root_dir)
                return account_generated_true
            else:
                shutil.rmtree(self.account_directory)
                return account_dir_exists_restored

    # update user's account values
    async def update(self):
        pass

    # confirm user's security
    async def authenticate(self):
        file = f'{self.account_directory}/{self.username}.db'

        if os.path.exists(file):
            database = sqlite3.connect(file)
            cursor = database.cursor()

            # passwords
            input_password = self.password.encode('utf-8')
            local_password: str = cursor.execute("""
            select json_extract(data, '$.password') from profile;
            """).fetchone()[0].encode('utf-8')

            # compare hashed passwords
            try:
                if bcrypt.checkpw(input_password, local_password):
                    return account_access_granted
                else:
                    return account_access_denied_password
            except ValueError as error:
                return account_access_denied_passwordhash

        else:
            if os.path.exists(self.account_directory):
                shutil.rmtree(self.account_directory)
                return account_dir_exists_restored
            else:
                return account_exists_false

    # pend account for deactivation
    async def deactivate(self):
        # confirm user security
        if os.path.exists(self.account_directory):
            # confirm user security
            if await self.authenticate() == account_access_granted:
                shutil.rmtree(self.account_directory)
                return account_deactivated_true
            else:
                return account_access_denied_password
        else:
            return account_exists_false

