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

            # accessible without any request to path "/"
            if path == "/":
                try:
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

            # requires request in json format
            try:
                # convert "data" to "dict"
                json_response: dict = json.loads(data)

                # specific user data
                user_profile: dict = json_response['profile']

                # ENSURE USERNAME IS LOWERCASE
                user_profile['username'] = user_profile['username'].lower()

                # ENSURE ACCOUNT VALUES ARE NOT EMPTY
                account_values = [user_profile['email'], user_profile['password'], user_profile['username']]
                for value in account_values:
                    if not value:
                        await websocket.send("Empty account value")
                        await websocket.close()
                        return None

                # ___________account traffic_____________
                # create new account
                if path == "/signup":
                    result = await RoomAccount(user_profile).create()
                    await websocket.send(str(result))

                # log in to account
                elif path == "/login":
                    authentication_result = await RoomAccount(user_profile).authenticate()

                    # user account directory path
                    account_directory_path = f'{root_dir}/system/user/account/{user_profile["username"]}'

                    if 'does not exist' in authentication_result:
                        await websocket.send(str(authentication_result))
                        await websocket.close()
                    elif 'Access granted' in authentication_result:
                        database = TinyDB(f'{account_directory_path}/{user_profile["username"]}.json')

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
                elif path == "/delete":
                    result = await RoomAccount(user_profile).delete()
                    if 'does not exist' in result:
                        await websocket.send(str(result))
                        await websocket.close()
                    else:
                        await websocket.send(str(result))

                # unrecognized path / route
                else:
                    pass  # pass route to room-traffic
                # ___________account traffic_____________

                # __________USER_SEARCH TRAFFIC__________
                if path == "/search/roommates":
                    authentication_result = await RoomAccount(user_profile).authenticate()

                    if 'Access granted' in authentication_result:
                        search_value = json_response['search_value']
                        search_result = Search().from_roommates(user_profile['username'], search_value)
                        await websocket.send(str(search_result))
                    elif 'does not exist' in authentication_result:
                        await websocket.send(str(authentication_result))
                        await websocket.close()
                    else:
                        await websocket.send(authentication_result)
                # __________USER_SEARCH TRAFFIC__________

                # ___________room traffic_____________
                if f"/{user_profile['username']}/room" in path:
                    authentication_result = await RoomAccount(user_profile).authenticate()
                    if 'does not exist' in authentication_result:
                        await websocket.send(str(authentication_result))
                        print(authentication_result)
                        await websocket.close()

                    elif 'Access granted' in authentication_result:
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
