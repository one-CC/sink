# -*- coding utf-8 -*-
# @Time : 2021/8/18 17:43
# @Author : donghao
# @File : models.py
# @Desc :
import asyncio
import time
import traceback
from datetime import datetime

import aiofiles
from aiofiles.threadpool import AsyncTextIOWrapper

from gps_transform import gps_transform
from utils import get_root_path

TIME_STAMP = 0.2
ROOT_PATH = get_root_path()


class Car:
    def __init__(self, car_number):
        self.car_number = car_number
        self.gps = None
        self.accelerate = None
        self.angle = None
        self.position = [0, 0]
        self.battery = 100
        self.connected = False

        self.__reader = None  # type: asyncio.StreamReader
        self.__writer = None  # type: asyncio.StreamWriter

    async def receive(self):
        file = await aiofiles.open('{0}/logs/car_logs/car_{1}_{2}.txt'.format(
            ROOT_PATH, self.car_number, datetime.now().strftime('%m_%d')), mode='a')  # type: AsyncTextIOWrapper
        await file.write("************* 开始测试，时间：" +
                         datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " *************" + '\n')
        try:
            while True:
                # 倒数最后一个数据包可能会被截断，将导致解析错误；
                # 设置 TCP 接收buffer大小
                data = await self.__reader.read(10240)
                if len(data) == 0:
                    break
                if len(data) >= 40:
                    # Car的每个包只包含一个ACC、Angle、GPS，包之间用一个#分隔，包内变量间用；分隔，变量的分量之间用，分隔
                    try:
                        messages = (data.decode('utf-8')).split('#')
                        variables = messages[-2].split(';')  # 最后一个是空字符串
                        v1 = variables[0].split(',')
                        v2 = variables[1].split(',')
                        v3 = variables[2].split(',')
                        self.accelerate = [float(v1[0]), float(v1[1]), float(v1[2])]
                        # xyz 东北天
                        self.angle = [float(v2[0]), float(v2[1]), float(v2[2])]
                        self.gps = [float(v3[0]), float(v3[1])]
                        self.position = gps_transform(self.gps)
                    except Exception:
                        print("包解析错误！")
                        traceback.print_exc()
                    format_str = "加速度：{0}    角度：{1}    GPS：{2}".format(self.accelerate, self.angle, self.gps)
                    time_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    await file.write("{0} ：{1}\n".format(time_string, format_str))
        except Exception:
            traceback.print_exc()
        finally:
            await file.write("************* 结束测试，时间：" +
                             datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " *************\n\n")
            await file.close()
            print("小车 {0} 的tcp连接已断开！".format(self.car_number))
            self.close_car()

    async def send(self, messages: list, energy_consumption: float):
        try:
            for message in messages:
                self.__writer.write(message.encode('utf-8'))
                await self.__writer.drain()
                await asyncio.sleep(TIME_STAMP)
            self.battery = max(self.battery - energy_consumption, 0)
        except ConnectionResetError:
            print("小车 {0} 的tcp连接已断开！".format(self.car_number))
            self.close_car()

    def connect_car(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.connected = True
        self.__reader = reader
        self.__writer = writer

    def close_car(self):
        self.connected = False
        self.__reader = None
        if self.__writer is not None:
            self.__writer.close()
            self.__writer = None

    def __str__(self):
        return "Car:{0}".format(self.car_number)


class UWB:
    def __init__(self, uwb_number, gps):
        self.distance = 0
        self.uwb_number = uwb_number
        self.gps = gps
        self.position = gps_transform(gps)
        self.connected = False

        self.__reader = None  # type: asyncio.StreamReader
        self.__writer = None  # type: asyncio.StreamWriter

    async def receive(self):
        file = await aiofiles.open('{0}/logs/uwb_logs/uwb_{1}_{2}.txt'.format(
            ROOT_PATH, self.uwb_number, datetime.now().strftime('%m_%d')), mode='a')  # type: AsyncTextIOWrapper
        await file.write("************* 开始测试，时间：" +
                         datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " *************" + '\n')
        try:
            while True:
                data = await self.__reader.read(10240)
                if len(data) == 0:
                    break
                time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                await file.write("{0} 来自UWB {1} ：{2}\n".format(time_string, self.uwb_number, data.decode('utf-8')))

                # UBW的每个包只包含一个distance，包之间用一个#分隔
                messages = (data.decode('utf-8')).split('#')
                self.distance = float(messages[-2])  # 最后一个是空字符串
        except Exception:
            traceback.print_exc()
        finally:
            print("UWB {0} 的tcp连接已断开！".format(self.uwb_number))
            await file.write("************* 结束测试，时间：" +
                             datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " *************\n\n")
            await file.close()
            self.close_uwb()

    def get_distance(self):
        res = self.distance
        return res

    def connect_uwb(self, reader: asyncio.StreamReader):
        self.connected = True
        self.__reader = reader

    def close_uwb(self):
        self.distance = 0
        self.connected = False
        self.__reader = None

    def __str__(self):
        return "UWB:{0}".format(self.uwb_number)


