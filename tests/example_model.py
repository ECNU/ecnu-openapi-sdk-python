from dataclasses import dataclass
from datetime import datetime
from src.sample.sync import APIConfig, SyncToModel

@dataclass
class FakeRowsWithTS:
    created_at: datetime = None
    updated_at: datetime = None
    deleted_mark: int = None
    id: int = None #Python会自动处理整数的大小，无需显式指定长整型。
    userId: str = None
    name: str = None
    
def exampleSyncToModel():
    '''
		   api = APIConfig {
		   	APIPath        string   // 接口的地址，例如 /api/v1/sync/fakewithts, 也可以追加参数，例如 /api/v1/sync/fakewithts?id=1
		   	PageSize       int     // 翻页参数会自动添加，默认 pageSize 是 2000，最大值是 10000。
			BatchSize      int     // 批量写入数据时的批次大小，默认是100。给的太大可能会数据库报错，请根据实际情况调整。
			UpdatedAtField string                     // 增量同步时，数据库内的时间戳字段名，默认是 updated_at
		   }

	'''

	# 配置待同步的接口
    api = APIConfig(
        APIPath = "/api/v1/sync/fakewithts",
        PageSize = 2000
    )

    api.SetParam("ts", "0")

    # 同步到Model对象
    fakerows= FakeRowsWithTS()

    fakerows, err = SyncToModel(fakerows, api)

    if err != None :
        print(err)
        return
    print("Model: 已同步 ", len(fakerows), " 条数据\n")

    # 增量同步
    # 2023-09-28 00:00:00
    ts = 1672675200
    api.SetParam("ts", str(ts))
    api.SetParam("full", "1")

    fakerows, err = SyncToModel(fakerows, api)
    if err != None :
        print(err)
        return
    print("Model: 增量同步 ", len(fakerows), " 条数据\n")
    # print(dnsrecords)