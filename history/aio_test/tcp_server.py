# -*- coding utf-8 -*-
# @Time : 2021/8/17 15:24
# @Author : donghao
# @File : tcp_server.py
# @Desc : asyncio 网络IO API 测试
import asyncio

async def server(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    data = await reader.read(1024)
    addr = writer.get_extra_info('peername')
    print("收到来自{0}数据: {1}".format(addr, data.decode()))

    print("发送数据：", data.decode())

    writer.write(data)
    await writer.drain()

    writer.close()
    await writer.wait_closed()


async def main():
    sockets = await asyncio.start_server(server, "127.0.0.1", 8888)
    addr = sockets.sockets[0].getsockname()
    print("本机服务地址：", addr)

    async with sockets:
        await sockets.serve_forever()

asyncio.run(main())
