#!/usr/bin/env python
# encoding: utf-8
import os
import glob


# 转成xml格式
def convert_to_xml(dir):
    # 注意文件夹下面图片的格式是png, jpg, pdf
    file_paths_1 = glob.glob(dir + "/*.png")
    file_paths_2 = glob.glob(dir + "/*.jpg")
    file_paths_3 = glob.glob(dir + "/*.jpeg")

    file_xml_paths = glob.glob(dir + "/*.xml")
    for file in file_xml_paths:
        if len(file_paths_1) > 1:
            file_pic = file[:-4] + ".png"
        if len(file_paths_2) > 1:
            file_pic = file[:-4] + ".jpg"
        if len(file_paths_3) > 1:
            file_pic = file[:-4] + ".jpeg"
        file_csv = file[:-4] + ".csv"
        os.system("mv " + file + " ./xml/")
        os.system("mv " + file_pic + " ./done_pic/")
        os.system("mv " + file_csv + " ./csv/")

if __name__=='__main__':
    convert_to_xml("./")
