from __init__ import *

HOST = '127.0.0.1'
PORT = '5000'


# application path gateway
async def index(websocket, path: str):
    # on client's connection
    user_remote_address: tuple = websocket.remote_address
    # server work directory
    root_dir = os.getcwd()

    try:
        async for data in websocket:
            try:
                # convert "data" to "dict"
                json_response: dict = json.loads(data)

                # specific user data
                user_device = json_response['device']
                user_profile: dict = json_response['profile']

                # confirm user account security
                if path == "/":
                    accounts_parent_dir = os.listdir(f"{root_dir}/system/user/account")
                    # store all users found
                    users_from_all_databases = []

                    for directory in accounts_parent_dir:
                        os.chdir(f'{root_dir}/system/user/account/{directory}')
                        if os.path.isfile(f'{directory}.json'):
                            database = TinyDB(f'{directory}.json').table('profile')
                            # user profile with minimum data
                            user_profile = {
                                'username': database.all()[0]['username'],
                                'email': database.all()[0]['email'],
                                'country': database.all()[0]['country'],
                                'race': database.all()[0]['race'],
                                'hobbies': database.all()[0]['hobbies'],
                                'health': database.all()[0]['health'],
                            }
                            users_from_all_databases.append(user_profile)
                        else:
                            shutil.rmtree(f'{root_dir}/system/user/account/{directory}')
                        # restore root directory
                        os.chdir(root_dir)
                    # send users to client
                    await websocket.send(str(users_from_all_databases))

                # create new account
                elif path == "/signup":
                    result = await RoomAccount(user_profile).create()
                    await websocket.send(str(result))

                # log in to account
                elif path == "/login":
                    authentication_result = await RoomAccount(user_profile).authenticate()

                    # user account directory path
                    account_directory_path = f'{root_dir}/system/user/account/{user_profile["email"]}'

                    if 'does not exist' in authentication_result:
                        await websocket.send(str(authentication_result))
                        await websocket.close()
                    elif 'Access granted' in authentication_result:
                        database = TinyDB(f'{account_directory_path}/{user_profile["email"]}.json')

                        # user profile
                        profile = database.table('profile').all()[0]
                        profile.pop('password')  # remove password for security purposes

                        database_tables = {
                            'profile': profile
                        }
                        # send everything from database to user/client
                        await websocket.send(str(database_tables))
                    else:
                        await websocket.send(str(authentication_result))

                # pend deactivate account
                elif path == "/deactivate":
                    result = await RoomAccount(user_profile).deactivate()
                    if 'does not exist' in result:
                        await websocket.send(str(result))
                        await websocket.close()
                    else:
                        await websocket.send(str(result))

                # ___________room traffic_____________
                elif path == f"/user/{user_profile['username']}/room":
                    authentication_result = await RoomAccount(user_profile).deactivate()
                    if 'does not exist' in authentication_result:
                        await websocket.send(str(result))
                        await websocket.close()
                    else:
                        await websocket.send(str(result))
                # ___________room traffic_____________

                # unrecognized path / route
                else:
                    await websocket.send('Unknown address! Use \'/\' instead.')
                    await websocket.close()

            # if data is not type(dict)
            except json.decoder.JSONDecodeError as error:
                await websocket.send(f'Json error: {error}')

    # on client's disconnection
    except websockets.exceptions.ConnectionClosedError:
        print(user_remote_address, 'disconnected')


# application server
async def rooms_server():
    async with websockets.serve(index, HOST, PORT):
        await asyncio.Future()  # run forever


# exec application
if __name__ == '__main__':
    try:
        print(f'[Rooms]: Listening on (ws://{HOST}:{PORT}) OS:{sys.platform}.')
        asyncio.run(rooms_server())
    except KeyboardInterrupt:
        print('[Rooms]: Server forced to stop.')
