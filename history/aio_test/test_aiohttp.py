# -*- coding utf-8 -*-
# @Time : 2021/8/2 17:37
# @Author : donghao
# @File : test_aiohttp.py
# @Desc : 测试 requests 和 aiohttp 速度，耗时：aiohttp < requests (Session是否在request函数中无较大影响)
import asyncio
import requests
import aiohttp
import time

def request():
    response = requests.get("http://httpbin.org/get")
    text = response.text

def request_many():
    for _ in range(10):
        request()


async def async_request(session):
    response = await session.get("http://httpbin.org/get")
    text = await response.text()


async def async_request_many():
    task = []
    session = aiohttp.ClientSession()
    for _ in range(10):
        task.append(async_request(session))
    await asyncio.gather(*task)
    await session.close()

if __name__ == '__main__':
    start1 = time.time()
    request_many()
    print("同步耗时：" + str(time.time() - start1))
    start2 = time.time()
    asyncio.run(async_request_many())
    print("异步耗时：" + str(time.time() - start2))












