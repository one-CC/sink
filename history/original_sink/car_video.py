#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2019-12-30 21:32
# @Author  : lynch
import cv2


class CatchUsbVideo:
    def __init__(self, window_name='wsn_video', camera_idx='http://192.168.50.1:8080/?action=stream'):
        self.WINDOW_NAME = window_name
        self.CAMERA_IDX = camera_idx

    def get_camera(self):
        """
        摄像视频显示
        """
        cv2.namedWindow(self.WINDOW_NAME)

        # 视频来源
        try:
            cap = cv2.VideoCapture(self.CAMERA_IDX)
            success, frame = cap.read()
            while success and cv2.waitKey(1) == -1:
                # while cap.isOpened():
                ok, frame = cap.read()  # 读取一帧数据
                if not ok:
                    break
                    # 显示图像
                cv2.imshow(self.WINDOW_NAME, frame)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            cap.release()
        finally:
            print("camera连接已断开！")
            # 释放摄像头并销毁所有窗口
            cv2.destroyAllWindows()


if __name__ == '__main__':
    cv = CatchUsbVideo()
    cv.get_camera()
