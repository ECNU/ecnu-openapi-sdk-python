from dataclasses import dataclass
from datetime import datetime
from src.sample.sync import APIConfig, SyncToModel

@dataclass
class ZZJG:
    departmentId: str = None
    department: str = None
    parentId: str = None
    status: str = None
    isSt: str = None
    level: int = None

@dataclass
class Dnsrecord:
    created_at: datetime = None
    updated_at: datetime = None
    deleted_mark: int = None
    id: int = None #Python会自动处理整数的大小，无需显式指定长整型。
    userId: str = None
    name: str = None
    
def exampleSyncToModel():
    '''
		   type APIConfig struct {
		   	APIPath        string   // 接口的地址，例如 /api/v1/organization/list, 也可以追加参数，例如 /api/v1/organization/list?departmentId=0445
		   	PageSize       int     // 翻页参数会自动添加，默认 pageSize 是 2000，最大值是 10000。
			BatchSize      int     // 批量写入数据时的批次大小，默认是100。给的太大可能会数据库报错，请根据实际情况调整。
			UpdatedAtField string                     // 增量同步时，数据库内的时间戳字段名，默认是 updated_at
		   }

	'''

	# 配置待同步的接口
    api = APIConfig(
        APIPath = "/api/v1/organization/list",
        PageSize = 2000
    )
    # 同步到Model对象
    zzjgs= ZZJG()

    zzjgs, err = SyncToModel(zzjgs, api)

    if err != None :
        print(err)
        return
    print(zzjgs)
    print("Model: 组织机构同步 ", len(zzjgs), " 条数据\n")

    # 增量同步
    api = APIConfig(
        APIPath = "/api/v1/sync/fakewithts",
        PageSize = 2000
    )

    dnsrecords= Dnsrecord() #转换的Model类型

    # 2023-09-28 00:00:00
    ts = 1672761600
    api.SetParam("ts", str(ts))
    api.SetParam("full", "1")

    dnsrecords, err = SyncToModel(dnsrecords, api)
    if err != None :
        print(err)
        return
    print("Model: DNS记录增量同步 ", len(dnsrecords), " 条数据\n")
    # print(dnsrecords)