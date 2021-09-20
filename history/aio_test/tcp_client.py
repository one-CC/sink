# -*- coding utf-8 -*-
# @Time : 2021/8/17 15:24
# @Author : donghao
# @File : tcp_client.py
# @Desc : asyncio 网络IO API 测试
import asyncio

async def client_method(message):
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)
    print("发送消息：", message)
    writer.write(message.encode())

    data = await reader.read(1024)
    print("接收到消息：", data.decode())

    writer.close()
    await writer.wait_closed()

asyncio.run(client_method("Hello World!"))
