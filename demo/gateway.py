"""Fixed-destination localhost gateway; no arbitrary forwarding or target input."""
import asyncio
import json
import signal

ROUTES = {8000: ('demo',8000), 7474: ('neo4j',7474), 7687: ('neo4j',7687)}

async def relay(source, destination):
    while chunk := await source.read(65536):
        destination.write(chunk)
        await destination.drain()

async def connection(reader, writer, target):
    upstream = None
    tasks = []
    try:
        other, upstream = await asyncio.wait_for(asyncio.open_connection(*target),timeout=5)
        tasks = [asyncio.create_task(relay(reader,upstream)),asyncio.create_task(relay(other,writer))]
        done, pending = await asyncio.wait(tasks,return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            task.result()
    except (OSError,asyncio.TimeoutError) as exc:
        print(json.dumps({'event':'gateway_connection_error','correlation_id':'gateway','error':str(exc)}),flush=True)
    finally:
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks,return_exceptions=True)
        writer.close()
        if upstream:
            upstream.close()

async def main():
    stopping = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGTERM,signal.SIGINT):
        loop.add_signal_handler(signum,stopping.set)
    servers = []
    for port,target in ROUTES.items():
        async def accept(reader,writer,target=target):
            await connection(reader,writer,target)
        servers.append(await asyncio.start_server(accept,'0.0.0.0',port))
    await stopping.wait()
    for server in servers:
        server.close()
        await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
