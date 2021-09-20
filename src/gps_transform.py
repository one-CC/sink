# -*- coding: utf-8 -*-
# @Time : 2020/10/26 17:48
# @Author : DH
# @Site : 
# @File : gps_transform.py
# @Software: PyCharm
from pyproj import CRS, Transformer
# 48:102E~108E;   49:108E~114E
# 每个经度投影带，中央经度为500 000米，东加西减；
# 326xx:北半球;  327xx:南半球
# 对北半球，赤道为0米，北加南减；对南半球，赤道为10 000 000米，北加南减；
# 成都：104.07E,30.67W

# 涉及到转换的两个坐标：gps坐标与投影坐标
crs = CRS.from_epsg(4326)
crs_cs = CRS.from_epsg(32648)


def gps_transform(gps):
    """
    将GPS坐标转换为直角坐标
    :param gps: 要转换的gps
    :return:    以list表示的转换后的直角坐标
    """
    # 生成从 gps 坐标到投影坐标的转换器
    transformer = Transformer.from_crs(crs, crs_cs)
    loc = list(transformer.transform(gps[1], gps[0]))
    loc[0] = round(loc[0], 2)
    loc[1] = round(loc[1], 2)
    return loc


def position_transform(position):
    """
    将直角坐标转换为GPS坐标
    :param position: 要转换的投影坐标
    :return: gps坐标
    """
    # 生成从投影坐标到 gps 坐标的转换器
    transformer = Transformer.from_crs(crs_cs, crs)
    gps = list(transformer.transform(position[0], position[1]))
    # 上式的返回结果中的经纬度需要进行对调
    gps[1], gps[0] = round(gps[0], 5), round(gps[1], 5)
    return gps


if __name__ == '__main__':
    gps1 = [103.92972, 30.75184]
    gps2 = [103.92977, 30.75151]
    pos1 = gps_transform(gps1)
    pos2 = gps_transform(gps2)
    g1 = position_transform(pos1)
    g2 = position_transform(pos2)
    print(g1)
    print(g2)
    # print('GPS[103.92972, 30.75184]由UTM转化为直角坐标:', pos1)
    # print('GPS[103.92977, 30.75151]由UTM转化为直角坐标:', pos2)
    # print('两个点的直线距离为：', math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2))

