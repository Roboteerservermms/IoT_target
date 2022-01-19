import asyncio
import pathlib
import ssl
import websockets

VLC_HTTP_URL = localhost:9090
USER_ORDER = 0
SCHEDULE_ORDER = 1
SENSOR_ORDER = 2
GPIO_ORDER = 3

playlist = {
    "gpio" : [],
    "schedule" : []
}

# 클라이언트 접속이 되면 호출된다.
async def accept(websocket, path):
    while True:
    # 클라이언트로부터 메시지를 대기한다.
        data = await websocket.recv()
        if path == "gpio":
            
            # 클라인언트로 echo를 붙여서 재 전송한다.
            # 여기에 order별 vlc http command 전송
            # 웹 소켓 서버 생성.호스트는 localhost에 port는 9998로 생성한다.
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# ssl_context.load_cert_chain( pathlib.Path(__file__).with_name('localhost.pem'))
# vlc_control_server = websockets.serve(accept, "0.0.0.0", 9998,ssl=ssl_context)
vlc_control_server = websockets.serve(accept, "0.0.0.0", 9998)
# 비동기로 서버를 대기한다.
asyncio.get_event_loop().run_until_complete(vlc_control_server)
asyncio.get_event_loop().run_forever()