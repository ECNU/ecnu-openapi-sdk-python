import os
import csv
from dataclasses import dataclass, field
from typing import List

def ParseRowsToCSV(rows, filename):
    if len(rows) == 0 :
        return Exception("rows is empty")

    if filename == "" or filename == None :
        return Exception("filename is empty")
    # 获取当前路径
    curentPath = os.getcwd()
    # 判断文件是否已经存在
    # if os.path.exists(curentPath + "/" + filename) :
    #     return Exception("filename is exists")
    # 创建文件
    filePath = curentPath + "/" + filename
    temp = rows[0]
    a = []

    for headers in sorted(temp.keys()):
        a.append(headers)
    header = a
    # 将rows中的所有值转换为字符串
    for row in rows:
        for key, value in row.items():
            row[key] = str(value)

    with open(filePath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)  # 提前预览列名，当下面代码写入数据时，会将其一一对应。
        writer.writeheader()  # 写入列名
        writer.writerows(rows)  # 写入数据
    
    return None

def map_dict_to_dataclass(item, data_class):
    # 创建一个数据类对象，初始值均为None
    data_object = data_class

    # 获取数据类的字段名称
    fields = list(vars(data_class).keys())

    # 遍历字典的键值对，并映射到数据类的属性
    for field_name in fields:
        if field_name in item:
            setattr(data_object, field_name, item[field_name])

    return data_object

def UnmarshalRows(src, data_class):
    data_model = []
    try:
        for item in src:
            data_object = map_dict_to_dataclass(item, data_class)
            data_model.append(data_object)
    except Exception as e:
        return None, Exception(str(e))

    return data_model, None
