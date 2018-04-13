#!/usr/bin/env python
# encoding: utf-8
import os
import glob
import json

import fire
from bs4 import BeautifulSoup
import csv
import pandas
import xml.etree.ElementTree as ET
import shutil
import eventlet


eventlet.monkey_patch()
# 转成xml格式
def convert_to_xml(dir):
    # 注意文件夹下面图片的格式是png, jpg, pdf
    file_paths_1 = glob.glob(dir + "/*.png")
    file_paths_2 = glob.glob(dir + "/*.jpg")
    file_paths_3 = glob.glob(dir + "/*.jpeg")
    file_paths = file_paths_1 + file_paths_2 + file_paths_3

    for file in file_paths:
        file_xmlname = file[:-4] + ".xml"
        flag = False
        try:
            with eventlet.Timeout(10,False):
                os.system("python process.py " + file + " -l ChinesePRC " + " -xml " + file_xmlname)
                flag = True
        except:
            flag = False
            pass
        try:
            if flag == False:
                with eventlet.Timeout(10,False):
                   os.system("python process.py " + file + " -l ChinesePRC " + " -xml " + file_xmlname)
        except:
           print(file_xmlname,"接口调用异常")

        if flag == False:
           print(file_xmlname,"接口调用异常")


# 转换成式
def convert_to_csv(dir):
    output_paths = glob.glob(dir + "/*.xml")
    for xml in output_paths:
        soup = BeautifulSoup(open(xml), "lxml")
        texts = soup.find_all("text")
        rows = []
        for text in texts:
            locations = text.find_all("line")
            for loc in locations:
                #bottom, left, right, top = loc['b'], loc['l'], loc['r'], loc['t'],
                bottom, left, right, top = loc.get('b','0'), loc.get('l','0'), loc.get('r','0'), loc.get('t','0')
                value = "".join(loc.get_text().replace("\n",""))
                row = [bottom, left, right, top, value]
                rows.append(row)
        csv_name = xml[:-4] + ".csv"
        with open(csv_name,"w") as csvfile:
            writer = csv.writer(csvfile)
            #先写入columns_name
            writer.writerow(["bottom", "left", "right", "top", "value"])
            #写入多行用writerows
            writer.writerows(rows)


# 处理csv生成对应的属性列表
def deal_csv(file):
    loc_info = pandas.read_csv(file, engine='python')
    loc_info["size_1"] = loc_info["right"] - loc_info["left"]
    loc_info["size_2"] = loc_info["bottom"] - loc_info["top"]
    loc_info = loc_info.drop("right",1)
    loc_info = loc_info.drop("bottom",1)
    loc_json = loc_info.to_json(orient='index')

    loc_list = []
    loc_dict = json.loads(loc_json)
    for loc in loc_dict.values():
        position = str(loc['left']) + ',' + str(loc['top'])
        size = str(loc['size_1']) + ',' + str(loc['size_2'])
        loc_value = {
                    "Position": position,
                    "Size": size,
                    "StrokeThickness": "1",
                    "Shape": "BasicShapes.Rectangle",
                    "Content": loc['value'],
                    "ItemKind": "DiagramShape"
                }
        loc_list.append(loc_value)

    return loc_list


# 调用数据接口
def generate_xml(xml_origin_name, xml_last_name, loc_list):
    tree = ET.parse(xml_origin_name)
    root = tree.getroot()
    children = root[0][0][0]

    for i in range(len(loc_list)):
        item_name = "Item"+str(i+2)
        ET.SubElement(children, item_name, loc_list[i])

    ET.dump(children)

    tree.write(xml_last_name)


# 程序调用主体
def main(dir):
    dir = dir.replace("\\", "/")
    # 图片转换成xml
    #convert_to_xml(dir)
    # xml提取信息到csv
    convert_to_csv(dir)
    # 处理csv生成新xml需要的属性值
    csv_paths = glob.glob(dir + "/*.csv")
    for csv in csv_paths:
        loc_list = deal_csv(csv)
        xml_origin_name = str(os.path.abspath(os.getcwd()))+'/xml_04_origin/'+csv.split("/")[-1][:-4] + '_origin.xml'
        xml_last_name = str(os.path.abspath(os.getcwd()))+'/xml_04_last/'+csv.split("/")[-1][:-4] + '_last.xml'
        try:
            generate_xml(xml_origin_name,xml_last_name,loc_list)
        except Exception as e:
            raise e


if  __name__ == '__main__':
    fire.Fire()
