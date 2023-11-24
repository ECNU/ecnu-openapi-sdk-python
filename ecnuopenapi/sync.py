import urllib.parse
import csv
import datetime
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from ecnuopenapi.oauth_init import OAuth2Config
from ecnuopenapi.model import HttpGet
from ecnuopenapi.api import getRows, getAllRows
from ecnuopenapi.parse import ParseRowsToCSV, UnmarshalRows,map_dict_to_dataclass
from dateutil.parser import parse

MAX_PAGE_SIZE = 2000

class APIConfig:
    def __init__(self, APIPath, PageSize=0, BatchSize=0, UpdatedAtField=None):
        self.APIPath = APIPath
        self.PageSize = PageSize
        self.BatchSize = BatchSize
        self.UpdatedAtField = UpdatedAtField
        self.params = {}

    def SetDefault(self):
        if self.PageSize == 0:
            self.PageSize = 2000
        if self.PageSize > MAX_PAGE_SIZE:
            self.PageSize = MAX_PAGE_SIZE
        if self.BatchSize == 0:
            self.BatchSize = 100
        if not self.UpdatedAtField:
            self.UpdatedAtField = "updated_at"

    def AddParam(self, key, value):
        self.params[key] = value

    def SetParam(self, key, value):
        self.params[key] = value

    def DelParam(self, key):
        if key in self.params:
            del self.params[key]
    
    def SetParamsToApiPath(self):
        if '?' in self.APIPath:
            for (key, value) in self.params.items():
                return self.APIPath + "&" + key + "=" + value
        else:
            apiPath = self.APIPath + "?"
            for (key, value) in self.params.items():
                apiPath = apiPath + key + "=" + str(value) + "&"
            return apiPath[0:-1] # 去掉多余的那个&符号

def SyncToCsv(csvFileName, api):
    api.SetDefault()
    apiPath = api.SetParamsToApiPath()
    rows, err = getAllRows(apiPath, api.PageSize)
    if err:
        return 0, err
    err = ParseRowsToCSV(rows, csvFileName)
    if err != None:
        return 0, err
    return len(rows), None

def SyncToModel(dataModel, api):
    api.SetDefault()
    apiPath = api.SetParamsToApiPath()
    # getAllRows
    rows, err = getAllRows(apiPath, api.PageSize)
    if err:
        return None, err
    data, err = UnmarshalRows(rows, dataModel)
    if err != None:
        return None, err
    return data, None

def SyncToDB(db, api, dataModel):
    api.SetDefault()
    apiPath = api.SetParamsToApiPath()

    try:
        # 创建数据库表
        dataModel.metadata.create_all(db)
    except Exception as e:
        return 0, len(data), Exception(str(e))

    try:
        # 创建Session
        Session = sessionmaker(bind=db)
        # 创建Session实例
        session = Session()
    except Exception as e:
        return 0, len(data), Exception(str(e))

    inserted_data_count = 0  # 用于跟踪成功插入的数据条数

    pageNum = 1
    totalRecordsNum = 0
    while True:
        data, err = getRows(apiPath, pageNum, api.PageSize)
        if err != None:
            return 0, len(data.Rows), err
        if data.Rows == None or len(data.Rows) == 0:
            break
        # 往数据库中同步
        try:
            for row in data.Rows:
                data_object = map_dict_to_dataclass(row, dataModel)
                session.add(dataModel(**data_object.__dict__))
                # 批量插入数据
            if len(session.new) % api.BatchSize == 0:
                session.flush()
                inserted_data_count += api.BatchSize
            # 刷入剩下的数据
            session.commit()
            # 没有抛出异常，则插入成功，插入条数则为列表长度
            inserted_data_count = len(data.Rows)
            pageNum += 1
            totalRecordsNum += len(data.Rows)
        except Exception as e:
            # 如果有重复数据，你可以选择忽略或更新现有数据
            session.rollback() # 出现问题回滚
            return 0, totalRecordsNum, Exception(str(e))
        
    session.close()
    return inserted_data_count, totalRecordsNum, None

def GetLastUpdatedTS(db, api, dataModel):
    api.SetDefault()
    session = Session(db, future=True)
    updatedAt = api.UpdatedAtField
    max_updated_at = session.query(func.max(getattr(dataModel, updatedAt))).scalar()

    if not max_updated_at:
        return 0
    print(type(max_updated_at))
    print(max_updated_at)
    if type(max_updated_at) == str:
        return int(parse(max_updated_at).timestamp())
    return int(max_updated_at.timestamp())
