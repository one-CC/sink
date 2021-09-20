# -*- coding utf-8 -*-
# @Time : 2021/5/29 17:15
# @Author : DH
# @File : server_for_uwbs_test.py
# @Software : PyCharm
# @Desc : 用于测试三个uwb的三角定位，不涉及小车控制
import socket
import threading
import traceback

from history.sync_sink.car_control import *
from history.sync_sink.models import Car, UWB
from src.gps_transform import *
from src.location import trilateration
from src.utils import *

ROOT_PATH = get_root_path()
total_car_number = 5
ip2CarNumber = {
    '192.168.31.99': 1,
    # '169.254.62.154': 2,
    '192.168.2.16': 3,
    '192.168.43.82': 4,
    '192.168.43.242': 5,
}

ip2UWB = {
    '192.168.43.253': 1,
    '192.168.43.141': 2,
    '127.0.0.1': 3,
}

car_map = {}
for i in range(1, total_car_number + 1):
    car_map[i] = Car(i)

uwb_map = {}
# 每次测试需要手动填入三个 uwb 的 gps 信息
uwb_gps = [[103.92792, 30.75436], [103.92768, 30.75445], [0, 0]]
for i in range(1, 4):
    uwb_map[i] = UWB(i, uwb_gps[i - 1])

lock = threading.Lock()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '192.168.43.230'
port = 8888
# host = '127.0.0.1'
# port = 6666
server.bind((host, port))
server.listen(total_car_number + 3)


# 监听小车和uwb的连接请求
def bind_socket():
    print("等待连接中...")
    while True:
        try:
            client, addr = server.accept()
            if client:
                lock.acquire()
                global car_map, uwb_map
                if ip2UWB.get(addr[0], None):
                    # 如果是UWBip地址，则需要建立单独的线程来控制uwb；
                    uwb_number = ip2UWB[addr[0]]
                    uwb = uwb_map[uwb_number]
                    # 如果对应uwb没有活跃的连接线程，则创建线程；否则，忽视。
                    if not uwb.connected:
                        uwb.socket = client
                        uwb.connected = True
                        thread = threading.Thread(target=uwb.receive)
                        thread.start()
                    print("UWB {0} 已连接！".format(uwb_number))
                elif ip2CarNumber.get(addr[0], None):
                    # 如果为小车地址；
                    car_number = ip2CarNumber[addr[0]]
                    car = car_map[car_number]
                    # 如果对应小车没有活跃的连接线程，则创建线程；否则，忽视。
                    if not car.connected:
                        car.socket = client
                        car.connected = True
                        thread = threading.Thread(target=car.receive)
                        thread.start()
                    print("小车 {0} 已连接！".format(car_number))
                    # send_msg = "你已经接入系统，" + str(addr[0]) + '！'
                    # buffersize = car.send(send_msg)
                    # print("发送了{0}个比特过去".format(buffersize))
                else:
                    pass
                lock.release()
        except:
            print("服务器取消监听了！！！")
            break


def main(control):
    file = open('{0}/logs/car_logs/car_cmd_{1}.txt'.format(ROOT_PATH,
                                                           datetime.now().strftime('%m_%d')), mode='a')
    file.write("************* 开始测试，时间：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
               + " *************" + '\n')
    # 首先需要等待三个 uwb 都连接上
    while not all_uwbs_connected(uwb_map):
        pass
    try:
        count = 0
        while count < 1000:
            d1 = uwb_map[1].get_distance()
            d2 = uwb_map[2].get_distance()
            d3 = uwb_map[3].get_distance()
            if d1 != 0 and d2 != 0 and d3 != 0:
                target_position = trilateration(uwb_map[1].position, uwb_map[2].position, uwb_map[3].position,
                                                d1, d2, d3)
                target_gps = position_transform(target_position)
                print(target_gps)
                # count += 1
                # time.sleep(0.1)
    except Exception:
        traceback.print_exc()
    finally:
        print("服务器关闭！")
        file.write("************* 结束测试，时间：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                   + " *************" + '\n\n')
        file.close()


if __name__ == '__main__':
    listen_thread = threading.Thread(target=bind_socket)
    listen_thread.setDaemon(True)
    listen_thread.start()
    main(control=True)



