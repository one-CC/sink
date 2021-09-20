# -*- coding utf-8 -*-
# @Time : 2021/5/29 17:15
# @Author : DH
# @Software : PyCharm
# @Desc : 一辆车追踪另一辆车的异步版本
import asyncio
import json
import socket
import traceback

import aiofiles
import aiohttp
from aiofiles.threadpool import AsyncTextIOWrapper

from car_control import *
from models import Car, UWB
from utils import get_root_path

ROOT_PATH = get_root_path()
total_car_number = 5
ip2CarNumber = {
    '127.0.0.1': 1,
    '192.168.43.64': 2,
    '192.168.43.40': 3,
    '192.168.43.242': 5,
}
ip2UWBNumber = {
    '192.168.43.253': 1,
    '192.168.43.141': 2,
    '192.168.43.142': 3,
}
car_map = {}
for i in range(1, total_car_number + 1):
    car_map[i] = Car(i)
uwb_map = {}
# 每次测试需要手动填入三个 uwb 的 gps 信息
uwb_gps = [[103.92792, 30.75436], [103.92768, 30.75445], [0, 0]]
for i in range(1, 4):
    uwb_map[i] = UWB(i, uwb_gps[i - 1])


def accept_socket(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    ip = writer.get_extra_info("peername")[0]
    global car_map, uwb_map
    if ip2UWBNumber.get(ip, None):
        # 如果是UWBip地址，则需要建立单独的线程来控制uwb；
        uwb_number = ip2UWBNumber[ip]
        uwb = uwb_map[uwb_number]
        # 如果对应uwb没有活跃的连接线程，则创建线程；否则，忽视。
        if not uwb.connected:
            uwb.connect_uwb(reader)
            asyncio.create_task(uwb.receive())
            print("UWB {0} 已连接！".format(uwb.uwb_number))
    elif ip2CarNumber.get(ip, None):
        # 如果为小车地址；
        car_number = ip2CarNumber[ip]
        car = car_map[car_number]
        # 如果对应小车没有建立连接，则连接并创建receive协程
        if not car.connected:
            car.connect_car(reader, writer)
            asyncio.create_task(car.receive())
            print("小车 {0} 已连接！".format(car.car_number))


async def listen_socket():
    """ 监听小车和uwb的连接请求 127.0.0.1"""
    server = await asyncio.start_server(accept_socket, host="192.168.43.230", port=8888, family=socket.AF_INET)
    print("等待连接中...")
    try:
        await server.serve_forever()
    finally:
        server.close()
        await server.wait_closed()


async def post_data(session: aiohttp.ClientSession):
    """ 上传各个小车的数据给后台服务器 """
    url = "http://192.168.43.35:8080/car/insert"
    headers = {'content-type': 'application/json'}
    data_list = []
    for car in car_map.values():
        if car.connected:
            base_map = dict()
            base_map["number"] = car.car_number
            base_map["gps"] = car.gps
            base_map["angle"] = car.angle
            base_map["battery"] = car.battery
            data_list.append(base_map)
    json_data = json.dumps(data_list)
    while True:
        if session.closed:
            break
        await session.post(url=url, data=json_data, headers=headers)
        print(json_data)
        await asyncio.sleep(2.0)


async def main():
    asyncio.create_task(listen_socket())
    cmd_log = await aiofiles.open('{0}/logs/car_logs/car_cmd_{1}.txt'.format(
        ROOT_PATH, datetime.now().strftime('%m_%d')), mode='a')  # type: AsyncTextIOWrapper
    await cmd_log.write("************* 开始测试，时间：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                        + " *************" + '\n')
    target_car = car_map[5]
    car = car_map[3]
    while not target_car.connected or not car.connected:
        await asyncio.sleep(0.1)

    session = aiohttp.ClientSession()
    asyncio.create_task(post_data(session))
    try:
        while True:
            # await asyncio.sleep(0.5)
            if car.gps is not None:
                info = await move_forward_target(car, target_car.position, variable_speed=True)
                await cmd_log.write(info + '\n')
    except Exception:
        traceback.print_exc()
    finally:
        print("服务器关闭！")
        await cmd_log.write("************* 结束测试，时间：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                            + " *************" + '\n\n')
        await cmd_log.close()
        await session.close()
        await asyncio.sleep(1.0)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("键盘中断！")
