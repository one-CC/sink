# -*- coding utf-8 -*-
# @Time : 2021/9/1 15:01
# @Author : donghao
# @File : test_aiofiles_rw.py
# @Desc : 一个简单的异步生产者消费者模型，用于测试异步读写文件
import asyncio
import aiofiles
from queue import Queue
from aiofiles.threadpool import AsyncTextIOWrapper


async def async_read(queue: Queue):
    asyncTextIOWrapper = \
        await aiofiles.open("./car_logs/car_{}.txt".format(1), mode='r', encoding='utf8')  # type: AsyncTextIOWrapper
    count = 0
    while count < 100:
        count += 1
        data = await asyncTextIOWrapper.readline()
        if len(data) == 0:
            queue.put("")
            break
        queue.put(data)
    await asyncTextIOWrapper.close()


async def async_write(queue: Queue):
    asyncTextIOWrapper = \
        await aiofiles.open("./car_logs/car_{}_test.txt".format(1), mode='a', encoding='utf8')  # type: AsyncTextIOWrapper
    while True:
        if queue.qsize() > 0:
            data = queue.get()
            if len(data) == 0:
                break
            await asyncTextIOWrapper.write(data)
        else:
            await asyncio.sleep(0.1)
    await asyncTextIOWrapper.close()

async def main():
    queue = Queue()
    asyncio.create_task(async_read(queue))
    asyncio.create_task(async_write(queue))
    await asyncio.sleep(2)
    print(queue.qsize())


if __name__ == '__main__':
    asyncio.run(main())






