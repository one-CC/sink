# -*- coding utf-8 -*-
# @Time : 2021/7/30 14:36
# @Author : donghao
# @File : test_utils.py
# @Desc : 这个文件存放测试时可能会使用到的方法或类
import random

from history.sync_sink.models import Car
from src.car_control import get_control


#  键盘读取类
class ControlKeyboard:
    def __init__(self, keyboard_input):
        self.KEYBOARD_INPUT = keyboard_input

    def get_control(self):
        """

        :return:
        """
        msg = []
        # 小车方向
        if self.KEYBOARD_INPUT == 'w':  # 前
            msg.append('$1,0,0,0,0,0,0,0,0#')
            msg.append('$0,0,0,0,0,0,0,0,0#')
        elif self.KEYBOARD_INPUT == 'x':  # 后
            msg.append('$2,0,0,0,0,0,0,0,0#')
            msg.append('$0,0,0,0,0,0,0,0,0#')
        elif self.KEYBOARD_INPUT == 'a':  # 左
            msg.append('$3,0,0,0,0,0,0,0,0#')
            msg.append('$0,0,0,0,0,0,0,0,0#')
        elif self.KEYBOARD_INPUT == 'd':  # 右
            msg.append('$4,0,0,0,0,0,0,0,0#')
            msg.append('$0,0,0,0,0,0,0,0,0#')
        elif self.KEYBOARD_INPUT == 'z':  # 左转
            msg.append('$0,1,0,0,0,0,0,0,0#')
            msg.append('$0,0,0,0,0,0,0,0,0#')
        elif self.KEYBOARD_INPUT == 'c':  # 右转
            msg.append('$0,2,0,0,0,0,0,0,0#')
            msg.append('$0,0,0,0,0,0,0,0,0#')
        elif self.KEYBOARD_INPUT == 's':  # 停
            msg.append('$0,0,0,0,0,0,0,0,0#')

        # 摄像头方向
        elif self.KEYBOARD_INPUT == 'i':  # 上
            msg.append('$0,0,0,0,3,0,0,0,0#')
            # msg.append('$0,0,0,0,8,0,0,0,0#')
        elif self.KEYBOARD_INPUT == 'm':  # 下
            msg.append('$0,0,0,0,4,0,0,0,0#')
            # msg.append('$0,0,0,0,8,0,0,0,0#')
        elif self.KEYBOARD_INPUT == 'j':  # 左
            msg.append('$0,0,0,0,6,0,0,0,0#')
            # msg.append('$0,0,0,0,8,0,0,0,0#')
        elif self.KEYBOARD_INPUT == 'l':  # 右
            msg.append('$0,0,0,0,7,0,0,0,0#')
            # msg.append('$0,0,0,0,8,0,0,0,0#')
        elif self.KEYBOARD_INPUT == 'k':  # 停
            msg.append('$0,0,0,0,8,0,0,0,0#')

        # 超声波控制
        elif self.KEYBOARD_INPUT == 'r':  # 左
            msg.append('$0,0,0,0,1,0,0,0,0#')
        elif self.KEYBOARD_INPUT == 't':  # 中
            msg.append('$0,0,0,0,0,0,0,0,1#')
        elif self.KEYBOARD_INPUT == 'y':  # 右
            msg.append('$0,0,0,0,2,0,0,0,0#')

        # 灯开关控制
        elif self.KEYBOARD_INPUT == 'v':  # 开
            msg.append('$0,0,0,0,0,0,1,0,0#')
        elif self.KEYBOARD_INPUT == 'b':  # 关
            msg.append('$0,0,0,0,0,0,8,0,0#')

        # 其他功能
        elif self.KEYBOARD_INPUT == 'f':  # 鸣笛
            msg.append('$0,0,1,0,0,0,0,0,0#')
        elif self.KEYBOARD_INPUT == 'g':  # 灭火
            msg.append('$0,0,0,0,0,0,0,1,0#')

        return msg


def target_move(target: Car, randomly: bool):
    """
    控制目标移动
    :param target: 目标小车
    :param randomly: 是否随机移动
    :return:
    """
    if randomly:
        # 方法一：随机轨迹
        msgs, energy_consumption = randomly_move()
    else:
        # 方法二：自定义轨迹
        msgs, energy_consumption = defined_move()
    if msgs is None:
        return
    target.send(msgs, energy_consumption)


def randomly_move():
    # 随机轨迹，概率：6/8 1/8 1/8
    control = ['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'w', 'z', 'c']
    cmd_index = random.randint(0, 11)
    cmd = control[cmd_index]
    return get_control(cmd)


# 自定义轨迹
defined_control = ['w'] * 50
def defined_move():
    msgs, energy_consumption = None, 0
    if len(defined_control) > 0:
        cmd = defined_control.pop()
        msgs, energy_consumption = get_control(cmd)
    return msgs, energy_consumption
