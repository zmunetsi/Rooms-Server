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
                # assign value "profile" to json_profile
                user_profile: dict = json_response['profile']

                # create new user account
                if path == "/":
                    result = await RoomAccount(user_profile).authenticate()
                    await websocket.send(str(result))

                elif path == "/signup":
                    result = await RoomAccount(user_profile).create()
                    await websocket.send(str(result))

                elif path == "/signin":
                    await RoomAccount(user_profile).authenticate()

                elif path == "/deactivate":
                    result = await RoomAccount(user_profile).deactivate()
                    await websocket.send(str(result))

                else:
                    await websocket.send('Unknown path!')

            # if data is not type(dict)
            except json.decoder.JSONDecodeError as error:
                print(f'[DATA TYPE]: {error}')
                return error

    # on client's disconnection
    except websockets.exceptions.ConnectionClosedError:
        pass


# application server
async def rooms_server():
    async with websockets.serve(index, HOST, PORT):
        await asyncio.Future()  # run forever


# exec application
if __name__ == '__main__':
    print(f'Listening on {HOST}:{PORT}.')
    asyncio.run(rooms_server())
