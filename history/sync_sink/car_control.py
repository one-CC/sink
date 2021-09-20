# -*- coding utf-8 -*-
# @Time : 2021/1/12 14:47
# @Author : DH
# @File : car_control.py
# @Software : PyCharm
import math
from datetime import datetime

from history.sync_sink.models import Car


def get_control(cmd: str):
    """
    根据cmd，返回相应的指令
    :param cmd:     要完成的动作
    :return:    控制小车的指令列表, 能耗
    """
    msg, energy_consumption = [], 0
    # 小车方向
    if cmd == 'w':  # 前
        msg.append('$1,0,0,0,0,0,0,0,0#')
        msg.append('$0,0,0,0,0,0,0,0,0#')
        energy_consumption = 0.4
    elif cmd == 'quick':  # 快速前
        msg.append('$5,0,0,0,0,0,0,0,0#')
        msg.append('$0,0,0,0,0,0,0,0,0#')
        energy_consumption = 0.6
    elif cmd == 'slow':  # 慢速前
        msg.append('$6,0,0,0,0,0,0,0,0#')
        msg.append('$0,0,0,0,0,0,0,0,0#')
        energy_consumption = 0.2
    elif cmd == 'x':  # 后
        msg.append('$2,0,0,0,0,0,0,0,0#')
        msg.append('$0,0,0,0,0,0,0,0,0#')
        energy_consumption = 0.4
    elif cmd == 'a':  # 左
        msg.append('$3,0,0,0,0,0,0,0,0#')
        msg.append('$0,0,0,0,0,0,0,0,0#')
        energy_consumption = 0.2
    elif cmd == 'd':  # 右
        msg.append('$4,0,0,0,0,0,0,0,0#')
        msg.append('$0,0,0,0,0,0,0,0,0#')
        energy_consumption = 0.2
    elif cmd == 'z':  # 左转
        msg.append('$0,1,0,0,0,0,0,0,0#')
        msg.append('$0,0,0,0,0,0,0,0,0#')
        energy_consumption = 0.2
    elif cmd == 'c':  # 右转
        msg.append('$0,2,0,0,0,0,0,0,0#')
        msg.append('$0,0,0,0,0,0,0,0,0#')
        energy_consumption = 0.2
    elif cmd == 's':  # 停
        msg.append('$0,0,0,0,0,0,0,0,0#')

    # 灯开关控制
    elif cmd == 'v':  # 开
        msg.append('$0,0,0,0,0,0,1,0,0#')
    elif cmd == 'b':  # 关
        msg.append('$0,0,0,0,0,0,8,0,0#')

        # 摄像头方向
    elif cmd == 'i':  # 上
        msg.append('$0,0,0,0,3,0,0,0,0#')
        # msg.append('$0,0,0,0,8,0,0,0,0#')
    elif cmd == 'm':  # 下
        msg.append('$0,0,0,0,4,0,0,0,0#')
        # msg.append('$0,0,0,0,8,0,0,0,0#')
    elif cmd == 'j':  # 左
        msg.append('$0,0,0,0,6,0,0,0,0#')
        # msg.append('$0,0,0,0,8,0,0,0,0#')
    elif cmd == 'l':  # 右
        msg.append('$0,0,0,0,7,0,0,0,0#')
        # msg.append('$0,0,0,0,8,0,0,0,0#')
    elif cmd == 'k':  # 停
        msg.append('$0,0,0,0,8,0,0,0,0#')

    # 超声波控制
    elif cmd == 'r':  # 左
        msg.append('$0,0,0,0,1,0,0,0,0#')
    elif cmd == 't':  # 中
        msg.append('$0,0,0,0,0,0,0,0,1#')
    elif cmd == 'y':  # 右
        msg.append('$0,0,0,0,2,0,0,0,0#')

    # 其他功能
    elif cmd == 'f':  # 鸣笛
        msg.append('$0,0,1,0,0,0,0,0,0#')
    elif cmd == 'g':  # 灭火
        msg.append('$0,0,0,0,0,0,0,1,0#')

    return msg, energy_consumption


def calculate_angle(vector: list):
    """
    计算一个向量与平面x轴的夹角
    :param vector: 向量
    :return: 与x轴的夹角，范围[0, 360]
    """
    dist = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    angle = math.degrees(math.acos(vector[0] / dist))
    angle = angle if vector[1] > 0 else 360 - angle
    return round(angle, 2)


def calculate_distance(s: list, t: list):
    """
    计算两点之间的距离，保留两位小数
    :param s:
    :param t:
    :return:
    """
    return round(math.sqrt((s[0] - t[0]) ** 2 + (s[1] - t[1]) ** 2), 2)


def move_forward_target(car: Car, target_position: list, variable_speed=False) -> str:
    """
    根据小车与目标的位置，进行移动
    :param variable_speed: 是否开启变速，默认不开启
    :param car: 移动的小车
    :param target_position: 目标的平面坐标
    :return: 日志记录字符串
    """
    vector = [target_position[0] - car.position[0], target_position[1] - car.position[1]]
    distance = calculate_distance(vector, [0, 0])
    msgs, energy_consumption = None, 0
    if distance <= 3:
        # 距离小于四米，则不移动
        msgs, energy_consumption = get_control("s")
        info = "Action：原地不动"
        car.send(msgs, energy_consumption)
        time_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " 小车" + str(car.car_number)
        return "{0}：{1}".format(time_string, info)
    angle = calculate_angle(vector)

    # 将小车的三维角度投影到平面坐标中
    projected_car_angle = car.angle[2] if car.angle[2] >= 0 else 360 + car.angle[2]

    # 根据小车的朝向与目标向量的夹角，分情况：
    angle_diff = projected_car_angle - angle
    # print("当前角度：", angle_diff)
    if math.fabs(angle_diff) <= 30 or math.fabs(angle_diff) >= 330:
        # 小夹角情况下，直接向前走
        info = "Action：直接向前走"
        if variable_speed and distance > 6:
            msgs, energy_consumption = get_control('quick')
        elif variable_speed and distance > 3:
            msgs, energy_consumption = get_control('w')
        else:
            msgs, energy_consumption = get_control("w")
    elif 30 < angle_diff <= 90 or -330 <= angle_diff < -270:
        # 右转
        info = "Action：右转"
        msgs, energy_consumption = get_control("d")
    elif -90 <= angle_diff < -30 or 270 <= angle_diff < 330:
        # 左转
        info = "Action：左转"
        msgs, energy_consumption = get_control("a")
    elif 90 < angle_diff <= 180 or -270 <= angle_diff < -180:
        # 原地右转
        info = "Action：原地右转"
        msgs, energy_consumption = get_control("c")
    elif -180 <= angle_diff < -90 or 180 < angle_diff < 270:
        # 原地左转
        info = "Action：原地左转"
        msgs, energy_consumption = get_control("z")
    car.send(msgs, energy_consumption)
    time_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " 小车" + str(car.car_number)
    return "{0}：位置向量的角度：{1}\t小车朝向角度：{2}\t{3}".format(time_string, angle, projected_car_angle, info)


def top3_closest_cars(target_position: list, car_map: dict):
    """
    计算当前时刻距离目标最近的三个小车
    :param car_map:     小车字典
    :param target_position:     目标的平面坐标
    :return:    被选择的三个小车
    """
    selected_car = []
    score_map = dict()
    max_distance = 1
    for car in car_map.values():
        max_distance = max(max_distance, calculate_distance(car.position, target_position))
    for num, car in car_map.items():
        distance = calculate_distance(car.position, target_position)
        # 计算得分, 偏重于距离
        score = 0 if car.battery < 5 else 200 * (1 - distance / max_distance) + car.battery
        if score > 0:
            score_map[score] = car
    rank_map = sorted(score_map)
    selected_car.append(score_map[rank_map[0]])
    selected_car.append(score_map[rank_map[1]])
    selected_car.append(score_map[rank_map[2]])
    return selected_car
