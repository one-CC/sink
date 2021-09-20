# -*- coding: utf-8 -*-
# @Time : 2020/10/8 16:26
# @Author : DH
# @Site : 
# @File : location.py
# @Software: PyCharm
import numpy as np
import time
import matplotlib.pyplot as plt


def trilateration(p1, p2, p3, d1, d2, d3):
    """
    用于三角定位，返回定位的估计值。
    :param p1:  第一个点的坐标
    :param p2:  第二个点的坐标
    :param p3:  第三个点的坐标
    :param d1:  第一个点测得的距离
    :param d2:  第二个点测得的距离
    :param d3:  第三个点测得的距离
    :return:    以numpy数组表示的定位点的坐标 [x,y]
    """
    X = np.asarray([[p3[0] - p1[0], p3[1] - p1[1]], [p3[0] - p2[0], p3[1] - p2[1]]])
    Y = np.asarray([0.5 * (d1**2 - d3**2 + p3[0]**2 + p3[1]**2 - p1[0]**2 - p1[1]**2),
                    0.5 * (d2**2 - d3**2 + p3[0]**2 + p3[1]**2 - p2[0]**2 - p2[1]**2)])
    pos = np.dot(np.dot(np.linalg.inv(np.dot(X.T, X)), X.T), Y)
    return pos


if __name__ == '__main__':
    p1 = [0, 0]
    d1 = 5
    p2 = [15, 0]
    d2 = 10
    p3 = [5, 20]
    d3 = 20
    pos = trilateration(p1, p2, p3, d1, d2, d3)
    print(pos)
    # 可视化节点位置及其传感范围
    fig1 = plt.figure('fig1')
    x = [p1[0], p2[0], p3[0]]
    y = [p1[1], p2[1], p3[1]]
    d = [d1, d2, d3]
    plt.scatter(x, y)
    plt.axis([-50, 50, -50, 50])
    for i in range(3):
        theta = np.arange(0, 2 * np.pi, 0.01)
        a = x[i] + d[i] * np.cos(theta)
        b = y[i] + d[i] * np.sin(theta)
        if i == 0:
            plt.plot(a, b, '--r')
        elif i == 1:
            plt.plot(a, b, '--c')
        else:
            plt.plot(a, b, '--k')
    plt.scatter(pos[0], pos[1])
    plt.grid()
    fig1.show()
    time.sleep(1)

