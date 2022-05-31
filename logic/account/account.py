import os

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

    # application root directory
    root_dir = os.getcwd()

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
                return {"result": account_exists_true}
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
                return {"result": account_generated_true}
            else:
                shutil.rmtree(self.account_directory)
                return {"result": account_dir_exists_restored}

    # update user's account values
    async def update(self):
        pass

    # confirm user's security
    async def authenticate(self):
        file = f'{self.account_directory}/{self.username}.db'

        if self.username != '':
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
                        return {"result": account_access_granted}
                    else:
                        return {"result": account_access_denied_password}
                except ValueError as error:
                    return {"result": account_access_denied_passwordhash}

            else:
                if os.path.exists(self.account_directory):
                    shutil.rmtree(self.account_directory)
                    return {"result": account_dir_exists_restored}
                else:
                    return {"result": account_exists_false}
        else:
            if self.email != '':
                try:
                    accounts_parent_dir = os.listdir(f"system/user/account")
                    directory_index = 0
                    for directory in accounts_parent_dir:
                        if os.path.isdir(f'system/user/account/{directory}'):
                            os.chdir(f'system/user/account/{directory}')
                            if os.path.isfile(f'{directory}.db'):
                                # database
                                database = sqlite3.connect(f'{directory}.db')
                                cursor = database.cursor()

                                # user profile with minimum data
                                user_profile: dict = json.loads(cursor.execute("""
                                select json_extract(data, '$') from profile;
                                """).fetchone()[0])

                                # restore root-dir as work-dir
                                os.chdir(self.root_dir)

                                # passwords
                                input_password = self.password.encode('utf-8')
                                local_password: str = user_profile['password'].encode('utf-8')

                                TODO: "if no account have a matching email then return account_exists_false_value"

                                # increment directory index
                                directory_index += 1

                                # check for account with matching email & password
                                if user_profile['email']:
                                    if user_profile['email'] == self.email:
                                        if bcrypt.checkpw(input_password, local_password):
                                            return {
                                                "username": user_profile['username'],
                                                "result": account_access_granted}
                                        else:
                                            if directory_index == len(accounts_parent_dir):
                                                return {"result": account_access_denied_password}
                except FileNotFoundError:
                    # account-dir does not exist
                    return {"result": account_exists_false}
            else:
                # username & email have no values
                return {"result": account_exists_false}

    # pend account for deactivation
    async def deactivate(self):
        # confirm user security
        if os.path.exists(f'{self.account_directory}/{self.username}.db'):
            # confirm user security
            if await self.authenticate() == account_access_granted:
                shutil.rmtree(self.account_directory)
                return {"result": account_deactivated_true}
            else:
                return {"result": account_access_denied_password}
        else:
            if os.path.exists(self.account_directory):
                shutil.rmtree(self.account_directory)
                return {"result": account_dir_exists_restored}
            else:
                return {"result": account_exists_false}

