import uvicorn

APPLICATION_READY = False


async def app(scope, receive, send):
    if scope['type'] != 'http' or scope['path'] != '/healthz':
        await send({
            'type': 'http.response.start',
            'status': 404,
            'headers': [
                (b'content-type', b'text/plain; charset=utf-8'),
                (b'content-length', b'3'),
                (b'x-content-type-options', b'nosniff'),
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': b'404',
        })
        return

    if APPLICATION_READY:
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'text/plain; charset=utf-8'),
                (b'content-length', b'2'),
                (b'x-content-type-options', b'nosniff'),
                (b'cache-control', b'no-cache, no-store, must-revalidate'),
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': b'ok',
        })
    else:
        await send({
            'type': 'http.response.start',
            'status': 503,
            'headers': [
                (b'content-type', b'text/plain; charset=utf-8'),
                (b'content-length', b'3'),
                (b'x-content-type-options', b'nosniff'),
                (b'cache-control', b'no-cache, no-store, must-revalidate'),
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': b'bad',
        })


def setReady(state: bool) -> None:
    global APPLICATION_READY
    APPLICATION_READY = state


async def run() -> None:
    config = uvicorn.Config("opnsensek8sfirewall.health:app",
                            host="0.0.0.0",
                            port=8000, access_log=False)
    server = uvicorn.Server(config)
    await server.serve()
