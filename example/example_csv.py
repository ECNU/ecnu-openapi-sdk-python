from ecnuopenapi.sync import APIConfig, SyncToCsv

def exampleSyncToCSV():
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
    
	# 同步到 csv
	# csv 模式下，所有字段都会转为 string
    csvFile = "test.csv"

    rows, err = SyncToCsv(csvFile, api)
    if err != None :
        print(err)
        return
    print("CSV: 已同步 ", rows, " 条数据\n")