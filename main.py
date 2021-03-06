import json

from __init__ import *

HOST = '0.0.0.0'
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
                user_profile: dict = json_response['profile']

                # ENSURE ACCOUNT VALUES ARE NOT EMPTY
                try:
                    [user_profile['email'], user_profile['password'], user_profile['username']]
                except KeyError:
                    await websocket.send(str({"result": "empty account value"}))
                    await websocket.close()
                    return None

                # check for unwanted characters in username
                for char in user_profile['username']:
                    chars: str = "abcdefghijklmnopqrstuvwxyz_0123456789"
                    if char not in chars:
                        await websocket.send(str({"result": username_unwanted_character}))
                        await websocket.close()
                        return None

                # ENSURE USERNAME IS LOWERCASE
                user_profile['username'] = user_profile['username'].lower()

                # accessible without any request to path "/"
                if path == "/":
                    try:
                        accounts_parent_dir = os.listdir(f"{root_dir}/{databases_directory}")
                        # store all users found
                        users_from_all_databases = []

                        for directory in accounts_parent_dir:
                            os.chdir(f'{root_dir}/{databases_directory}/{directory}')
                            if os.path.isfile(f'{directory}.db'):
                                database = sqlite3.connect(f'{directory}.db')
                                cursor = database.cursor()

                                # user profile with minimum data
                                user_profile: dict = json.loads(cursor.execute("""
                                select json_extract(data, '$') from profile;
                                """).fetchone()[0])

                                # remove password from expose profile
                                user_profile.pop("password")

                                # append results
                                users_from_all_databases.append(user_profile)
                            else:
                                shutil.rmtree(f'{root_dir}/{databases_directory}/{directory}')
                            # restore root directory
                            os.chdir(root_dir)
                        # send users to client
                        if users_from_all_databases:
                            await websocket.send(str(users_from_all_databases))
                            await websocket.close()
                            break
                        else:
                            await websocket.send('No user found')
                            await websocket.close()
                            break
                    except FileNotFoundError:
                        await websocket.send('No user found')

                # ___________account traffic_____________
                # create new account
                if path == "/signup":

                    if len(user_profile['username']) >= 5:
                        if len(user_profile['password']) >= 8:
                            signup_result: dict = await RoomAccount(user_profile).create()

                            if user_profile['username'] != "":
                                if signup_result['result'] == account_exists_true:
                                    await websocket.send(str(signup_result))
                                    await websocket.close()
                                elif signup_result['result'] == username_unwanted_character:
                                    await websocket.send(str(signup_result))
                                    await websocket.close()
                                else:
                                    await websocket.send(str(signup_result))
                                    await websocket.close()
                        else:
                            # password < 8
                            await websocket.send(str({"result": "password is length less than 8"}))
                            await websocket.close()
                    else:
                        # username < 5
                        await websocket.send(str({"result": "username is length less than 5"}))
                        await websocket.close()

                # log in to account
                elif path == "/login":
                    authentication_result: dict = await RoomAccount(user_profile).authenticate()

                    # user account directory path
                    account_directory_path = f'{root_dir}/{databases_directory}/{user_profile["username"]}'

                    if authentication_result['result'] == account_exists_false:
                        await websocket.send(str(authentication_result))
                        await websocket.close()
                    elif authentication_result['result'] == account_access_granted:
                        user_account: str
                        if user_profile['username']:
                            user_account = user_profile['username']
                        else:
                            username = authentication_result['username']
                            user_account = username
                            account_directory_path = f'{root_dir}/{databases_directory}/{username}'

                        database = sqlite3.connect(f'{account_directory_path}/{user_account}.db')
                        cursor = database.cursor()

                        # user profile
                        profile: dict = json.loads(cursor.execute("""
                            select json_extract(data, '$') from profile;
                            """).fetchone()[0])
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
                    deactivation_result: dict = await RoomAccount(user_profile).deactivate()
                    if deactivation_result['result'] == account_exists_false:
                        await websocket.send(str(deactivation_result))
                        await websocket.close()
                    else:
                        await websocket.send(str(deactivation_result))

                # unrecognized path / route
                else:
                    pass  # pass route to room-traffic
                # ___________account traffic_____________

                # __________USER_SEARCH TRAFFIC__________
                if path == "/search/roommates":
                    authentication_result = await RoomAccount(user_profile).authenticate()

                    if authentication_result == account_access_granted:
                        search_value = json_response['search_value']
                        search_result = Search().from_roommates(user_profile['username'], search_value)
                        await websocket.send(str(search_result))
                    elif authentication_result == account_exists_false:
                        await websocket.send(str(authentication_result))
                        await websocket.close()
                    else:
                        await websocket.send(authentication_result)
                # __________USER_SEARCH TRAFFIC__________

                # ___________room traffic_____________
                if f"/{user_profile['username']}/room" in path:
                    authentication_result = await RoomAccount(user_profile).authenticate()
                    if authentication_result == account_exists_false:
                        await websocket.send(str(authentication_result))
                        print(authentication_result)
                        await websocket.close()

                    elif authentication_result == account_access_granted:
                        if path == f"/{user_profile['username']}/room/new":
                            room_response = Rooms(user_profile, json_response['room']).new_room()
                            await websocket.send(room_response)
                        elif path == f"/{user_profile['username']}/room/delete":
                            room_response = Rooms(user_profile, json_response['room']).delete_room()
                            await websocket.send(room_response)
                        elif path == f"/{user_profile['username']}/room/update":
                            room_response = Rooms(user_profile, json_response['room']).update_room()
                            await websocket.send(room_response)
                        elif path == f"/{user_profile['username']}/room/":
                            room_response = Rooms(user_profile, json_response['room']).get_rooms()
                            await websocket.send(str(room_response))
                        else:
                            await websocket.close()
                    else:
                        await websocket.send(str(authentication_result))
                else:
                    pass
                # ___________room traffic_____________

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
