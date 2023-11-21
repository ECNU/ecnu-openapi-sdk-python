from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from src.sample.sync import APIConfig, SyncToDB, GetLastUpdatedTS

Base = declarative_base()

# 创建一个模型类，用于映射数据库表 必须继承Base
class FakeRowsWithTs(Base):
    __tablename__ = 'dns_records'
    id = Column(Integer, primary_key=True)
    userId = Column(String(255))
    name = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_mark = Column(Integer, default=0)

def exampleSyncToDB():

    # 初始化数据库连接，根据需要更改连接字符串
    mysql_url = 'mysql+pymysql://username:password@ip:port/dbname'
    pg_url = 'postgresql+psycopg2://username:password@ip:port/dbname'
    oracle_url = 'oracle+cx_oracle://username:password@ip:port/sidname'
    sqlserver_url = 'mssql+pymssql://username:password@ip:port/dbname'

    db = create_engine(mysql_url)  # 这里使用MySQL作为示例

    # 配置待同步的接口
    api = APIConfig(
        APIPath = "/api/v1/sync/fakewithts",
        PageSize = 2000,
        BatchSize = 100
    )

    api.SetParam("ts", "0")

    # 全量同步，如果未创建表会自动根据 model 建表---建议全量同步前先删除原表
    # 因为python无法使用c/go的引用或者指针，所以返回结果多一个参数用来记录接口返回的数据数量

    # 删除某张表  建议全量同步每次都删除
    FakeRowsWithTs.metadata.drop_all(db)
    
    rows, totalNum, err = SyncToDB(db, api, FakeRowsWithTs)
    if err != None :
        print(err)
        return
    print("DB: 首次同步，从接口获取到 ", rows, " 条数据\n")

    # 增量同步

    # 获取数据库内最后一条时间戳
    ts = GetLastUpdatedTS(db, api, FakeRowsWithTs)
    print("最后一条时间戳：", ts)

	# 参照接口文档，添加full参数，获取包含删除的数据
	# 因此可以捕捉上游数据删除的情况，以软删除的形式记录到数据库

    api.SetParam("ts", str(ts))
    api.SetParam("full", "1")

    rows, totalNum, err = SyncToDB(db, api, FakeRowsWithTs)
    if err != None :
        print(err)
        return
    print("DB: 增量同步，从接口获取到 ", totalNum, " 条数据\n")




