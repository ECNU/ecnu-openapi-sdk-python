from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from src.sample.sync import APIConfig, SyncToDB, GetLastUpdatedTS

Base = declarative_base()

# 创建一个模型类，用于映射数据库表 必须继承Base
class ZZJG(Base):
    __tablename__ = 'zzjg'  # 替换为你的表名
    # id = Column(Integer, primary_key=True, autoincrement=True) #建议设置为自增
    departmentId = Column(String(255), primary_key=True) # String需要指定长度
    department = Column(String(255))
    parentId = Column(String(255))
    status = Column(String(255))
    isSt = Column(String(255))
    level = Column(Integer)

# 定义 Dnsrecord 模型
class Dnsrecord(Base):
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
        APIPath = "/api/v1/organization/list",
        PageSize = 2000,
        BatchSize = 100
    )

    # 全量同步，如果未创建表会自动根据 model 建表---建议全量同步前先删除原表
    # 因为python无法使用c/go的引用或者指针，所以返回结果多一个参数用来记录接口返回的数据数量

    # 删除某张表  建议全量同步每次都删除
    ZZJG.metadata.drop_all(db)
    
    rows, totalNum, err = SyncToDB(db, api, ZZJG)
    if err != None :
        print(err)
        return
    print("DB: 组织机构同步 ", rows, " 条数据\n")

    # 增量同步，以DNS记录同步为例
    api = APIConfig(
        APIPath = "/api/v1/sync/fakewithts",
        PageSize = 2000,
        BatchSize = 100,
        UpdatedAtField = "updated_at"
    )

    # 首次同步时，添加参数 ts=0，同步当前全部有效数据
	# 建议定期（1-2个月）也执行一次全量的有效数据同步，以避免过程中程序,网络等原因导致的增量任务不完整产生的数据丢失
    api.SetParam("ts", "0")
    api.SetParam("full", "1")

    rows, totalNum, err = SyncToDB(db, api, Dnsrecord)
    if err != None :
        print(err)
        return
    print("DB:DNS记录首次同步，从接口获取到 ", totalNum, " 条数据\n")
    print("DB:DNS记录首次同步，数据库内有效更新 ", rows, " 条数据\n")

    # 增量同步 根据时间戳
    api = APIConfig(
        APIPath = "/api/v1/sync/fakewithts",
        PageSize = 2000,
        BatchSize = 100,
        UpdatedAtField = "updated_at"
    )

    # 获取数据库内最后一条时间戳
    ts = GetLastUpdatedTS(db, api, Dnsrecord)
    print("DNS记录最后一条时间戳：", ts)

	# 参照接口文档，添加full参数，获取包含删除的数据
	# 因此可以捕捉上游数据删除的情况，以软删除的形式记录到数据库

    api.SetParam("ts", str(ts))
    api.SetParam("full", "1")

    rows, totalNum, err = SyncToDB(db, api, Dnsrecord)
    if err != None :
        print(err)
        return
    print("DB:DNS记录首次同步，从接口获取到 ", totalNum, " 条数据\n")
    print("DB:DNS记录首次同步，数据库内有效更新 ", rows, " 条数据\n")




