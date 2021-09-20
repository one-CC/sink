# -*- coding utf-8 -*-
# @Time : 2021/8/2 16:37
# @Author : donghao
# @File : aio_test.py
# @Desc : 测试 aiofiles 和普通 file 操作速度，只操作多个文件条件下，耗时：file < aiofiles
import asyncio
import aiofiles
import time


def write_files(index):
    with open("./history/test_{}.txt".format(index), mode='r') as file:
        for _ in range(1000):
            # file.write(str(index) * 1000 + "\n")
            file.read()


def write_many():
    start1 = time.time()
    for i in range(1, 10):
        write_files(i)
    time.sleep(5)
    print("同步耗时：" + str(time.time() - start1))


async def async_write(index):
    async with aiofiles.open("./history/async_test_{}.txt".format(index), mode='r') as file:
        for _ in range(1000):
            # await file.write(str(index) * 1000 + "\n")
            await file.read()

async def async_write_many():
    start2 = time.time()
    for i in range(1, 10):
        asyncio.create_task(async_write(i))
    while len(asyncio.all_tasks()) > 1:
        await asyncio.sleep(5)
    print("异步耗时：" + str(time.time() - start2))


if __name__ == '__main__':
    write_many()
    asyncio.run(async_write_many())


