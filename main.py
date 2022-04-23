from __init__ import *

HOST = '127.0.0.1'
PORT = '5000'


# application path gateway
async def index(websocket, path: str):
    # on client's connection
    user_remote_address: tuple = websocket.remote_address

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
                    result = await RoomAccount(user_profile).authenticate()

                    if 'Access denied' in result:
                        await websocket.send(str(result))
                        await websocket.close()
                    else:
                        await websocket.send(str(result))

                # create new account
                elif path == "/signup":
                    result = await RoomAccount(user_profile).create()
                    await websocket.send(str(result))

                # sign in to account
                elif path == "/signin":
                    await RoomAccount(user_profile).authenticate()

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
