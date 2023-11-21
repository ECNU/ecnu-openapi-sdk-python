from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Float, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from src.sample.sync import APIConfig, SyncToDB, SyncToModel
import datetime
from src.sample.api import getRows
import psutil
from dataclasses import dataclass
import sqlite3

Base = declarative_base()


# 性能测试--Model
@dataclass
class FakeRowsModel:
    colString1: str = None
    colString2: str = None
    colString3: str = None
    colString4: str = None
    colInt1: int = None
    colInt2: int = None
    colInt3: int = None
    colInt4: int = None
    colFloat1: float = None
    colFloat2: float = None
    colFloat3: float = None
    colFloat4: float = None
    colSqlTime1: datetime = None
    colSqlTime2: datetime = None
    colSqlTime3: datetime = None
    colSqlTime4: datetime = None

# DB Model
class FakeRows(Base):
    __tablename__ = 'fake'  # 替换为你的表名
    # id = Column(Integer, primary_key=True, autoincrement=True) #建议设置为自增
    id = Column(String(255), primary_key=True) # String需要指定长度
    colString1 = Column(String(255))
    colString2 = Column(String(255))
    colString3 = Column(String(255))
    colString4 = Column(String(255))
    colInt1 = Column(BigInteger)
    colInt2 = Column(BigInteger)
    colInt3 = Column(BigInteger)
    colInt4 = Column(BigInteger)
    colFloat1 = Column(Float)
    colFloat2 = Column(Float)
    colFloat3 = Column(Float)
    colFloat4 = Column(Float)
    colSqlTime1 = Column(DateTime)
    colSqlTime2 = Column(DateTime)
    colSqlTime3 = Column(DateTime)
    colSqlTime4 = Column(DateTime)

def exampleCallAPIPerformance(api) :
    start_time = datetime.datetime.now()
    print("单次接口调用开始，pageSize=", api.PageSize)

    result, err = getRows(api.APIPath, 1, api.PageSize)
    if err != None:
        print(err)

    end_time = datetime.datetime.now()
    print("单次接口调用结束，pageSize=", api.PageSize, "用时",(end_time - start_time).total_seconds(), "秒")

def exampleSyncPerformanceByModel(api) :
    start_time = datetime.datetime.now()
    print("Model: 首次同步开始")
    start_memory = psutil.virtual_memory().used
    # 同步到Model对象
    fakerows= FakeRowsModel()
    fakerows, err = SyncToModel(fakerows, api)
    if err != None :
        print(err)
        return
    end_memory = psutil.virtual_memory().used
    end_time = datetime.datetime.now()
    print("Model: 同步结束，获取", len(fakerows), "条数据", "用时", (end_time - start_time).total_seconds(), "秒, 分配了", (end_memory - start_memory) / (1024 * 1024), "MB内存")


def exampleSyncPerformanceByDB(api, db):
    # 删除需要同步的原表
    FakeRows.metadata.drop_all(db)
    
    start_time = datetime.datetime.now()

    print(db.url.database, "：首次同步开始")
    start_memory = psutil.virtual_memory().used
    rows, totalNum, err = SyncToDB(db, api, FakeRows)
    if err != None :
        print(err)
        return

    end_memory = psutil.virtual_memory().used
    end_time = datetime.datetime.now()
    print(db.url.database, "：首次同步完成，全量插入用时", (end_time - start_time).total_seconds(), "秒, 分配了", (end_memory - start_memory) / (1024 * 1024), "MB内存")

    # 测试更新性能
    FakeRows.metadata.drop_all(db)
    print(db.url.database, "：第二次同步开始")
    rows, totalNum, err = SyncToDB(db, api, FakeRows)
    if err != None :
        print(err)
        return

    end_time = datetime.datetime.now()
    print(db.url.database, "：第二次同步完成，全量插入用时", (end_time - start_time).total_seconds(), "秒, 分配了", (end_memory - start_memory) / (1024 * 1024), "MB内存")


def exampleSyncPerformance():
    # 配置待同步的接口
    api = APIConfig(
        APIPath = "/api/v1/sync/fake",
        PageSize = 2000,
        BatchSize = 100
    )
    api.SetParam("totalNum", "10000")

    # 初始化数据库连接，根据需要更改连接字符串
    mysql_url = 'mysql+pymysql://username:password@ip:port/dbname'
    pg_url = 'postgresql+psycopg2://username:password@ip:port/dbname'
    oracle_url = 'oracle+cx_oracle://username:password@ip:port/sidname'
    sqlserver_url = 'mssql+pymssql://username:password@ip:port/dbname'

    # 获取一开始的内存信息
    start_memory = psutil.virtual_memory().used

    #
    exampleCallAPIPerformance(api)
    exampleSyncPerformanceByModel(api)
    #

    db1 = create_engine(mysql_url)
    exampleSyncPerformanceByDB(api, db1)
    # db2 = create_engine(pg_url)
    # exampleSyncPerformanceByDB(api, db2)
    # db3 = create_engine(sqlserver_url)
    # exampleSyncPerformanceByDB(api, db3)
    # db4 = create_engine(oracle_url)
    # exampleSyncPerformanceByDB(api, db4)

    # 最后结束时的内存信息
    end_memory = psutil.virtual_memory().used
    print("分配", (end_memory - start_memory) / (1024 * 1024), "MB内存")
