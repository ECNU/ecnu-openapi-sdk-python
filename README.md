# Python-SDK

## 能力
- 授权模式（token 管理）
    - [x] client_credentials 模式
    - [ ] password 模式
    - [ ] authorization code 模式
- 接口调用
    - [x] GET
    - [ ] POST
    - [ ] PUT
    - [ ] DELETE
- 数据同步（接口必须支持翻页）
    - 全量同步
        - [x] 同步为 csv 格式
        - [ ] 同步为 xls/xlsx 格式
        - [x] 同步到数据库
        - [x] 同步到模型
    - 增量同步（接口必须支持ts增量参数）
        - [x] 同步到数据库
        - [x] 同步到模型

## 依赖
- python 3.10 +
- [requirements.txt](requirements.txt)



## 相关资料
- [oauth2.0](https://oauth.net/2/)
- [sqlalchemy](https://www.sqlalchemy.org/)
## 支持的数据库
理论上只要 sqlalchemy支持的数据库驱动都可以支持，以下是测试的情况

如果sqlalchemy无法直接支持，可以先同步到模型，然后自行处理数据入库的逻辑。

| 数据库        | 驱动                     | 测试情况 | upsert 支持 |
|------------|----------------------------| --- | --- |
| MySQL      | pymysql                    | 测试通过 | todo |
| SQLite     | null                       | 测试通过 | todo |
| PostgreSQL | psycopg2                   | 测试通过 | todo |
| SQL Server | pymssql                    | 测试通过 | todo |
| Oracle     | cx_oracle                  | 测试通过 | todo |

## 示例

### 安装 sdk
```bash
$pip install ecnu-openapi-sdk-python
```
### 接口调用
初始化 SDK 后直接调用接口即可，sdk 会自动接管 token 的有效期和续约管理。

```python
from ecnuopenapi.oauth_init import OAuth2Config, initOauth2ClientCredentials
from ecnuopenapi.model import callAPI

config = OAuth2Config(
        client_id="client_id",
        client_secret="client_secret",
    )
initOauth2ClientCredentials(config)
print(callAPI('https://api.ecnu.edu.cn/api/v1/sync/fakewithts?ts=0&pageSize=1&pageNum=1', 'GET'))
```

### 数据同步
首先初始化 SDK 
然后只需要定义好 orm 映射，SDK 会接管接口调用，数据表创建，数据同步等所有工作。

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from ecnuopenapi.sync import APIConfig, SyncToDB
from ecnuopenapi.oauth_init import OAuth2Config, initOauth2ClientCredentials
Base = declarative_base()

# 创建一个模型类，用于映射数据库表 必须继承Base
class FakeRowsWithTs(Base):
    __tablename__ = 'fake_rows_with_ts'
    id = Column(Integer, primary_key=True)
    userId = Column(String(255))
    name = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_mark = Column(Integer, default=0)

sqlite_url = 'sqlite:///test.db'
db = create_engine(sqlite_url) 

api = APIConfig(
        APIPath = "/api/v1/sync/fakewithts",
        PageSize = 2000,
        BatchSize = 100
 )

api.SetParam("ts", "0")

print(SyncToDB(db, api, FakeRowsWithTs))
```

详见以下示例代码，和示例代码中的相关注释

- [Init & CallAPI](tests/example.py)
- [SyncToCSV](tests/example_csv.py)
- [SyncToModel](tests/example_model.py)
- [SyncToDB](tests/example_db.py)


## 性能

性能与 ORM 的实现方式（特别是对 upsert 的实现方式），数据库的实现方式，以及网络环境有关，不一定适用于所有情况。

当同步到数据库时，SDK 会采用分批读取/写入的方式，以减少内存的占用。

当同步到模型时，则会将所有数据写入到一个数组中，可能会占用较大的内存。

以下是测试环境

### 同步程序运行环境
- i5 cpu
- 32G 内存
- windows10 X64
- WD 固态硬盘
- dotnet 4.8

### 测试接口信息
- /api/v1/sync/fake
- 使用 pageSize=2000 仅限同步
- 接口请求耗时约 0.2 - 0.3 秒
- 接口数据示例

```json
{
	"errCode": 0,
	"errMsg": "success",
	"requestId": "73a60094-c0f1-4daf-bc58-4626fbef7a2b",
	"data": {
		"pageSize": 2000,
		"pageNum": 1,
		"totalNum": 10000,
		"rows": [{
			"id": 1,
			"colString1": "Oxqmn5MWCt",
			"colString2": "mzavQncWeNlOlFgUW7HC",
			"colString3": "mvy6K1HU7rdCicPbvvA3rNZcDWPhvV",
			"colString4": "XGsK5NVQHOu4JrmHZ9ZL1iLf0UYpdIvNIzswULzb",
			"colInt1": 3931594532918648027,
			"colInt2": 337586114254574578,
			"colInt3": 2291922259603323213,
			"colInt4": 3000562485500051124,
			"colFloat1": 0.46541339000557547,
			"colFloat2": 0.6307996439929248,
			"colFloat3": 0.9278393850101392,
			"colFloat4": 0.7286866920659677,
			"colSqlTime1": "2023-10-20 22:02:07",
			"colSqlTime2": "2023-10-20 22:02:07",
			"colSqlTime3": "2023-10-20 22:02:07",
			"colSqlTime4": "2023-10-20 22:02:07"
		}]
	}
}
```

### 测试结果
- 数据库：本地mysql:5.7 (docker环境)
- pageSize = 2000
- batchSize = 100

| 数据量(`totalNum`) | Time Spent on `Direct CallAPI` | Time Spent on `Model Sync ` | Time Spent on `DB Sync ` |
| ------------------ | ------------------------------ | --------------------------- | ------------------------ |
| `1w`               | 0.324615                       | 1.192462                    | 6.551163                 |
| `10w`              | 0.280315                       | 7.836467                    | 30.583456                |
| `100w`             | 0.28313                        | 78.528211                   | 263.68381                |

| 数据量(`totalNum`) | Memory Spent on `Model Sync ` | Memory Spent on `DB Sync ` |
| ------------------ | ----------------------------- | -------------------------- |
| `1w`               | 3.07421875                    | 3.12890625                 |
| `10w`              | 107.265625                    | 15.22265625                |
| `100w`             | 695.171875                    | 12.56640625                |


## 注意事项

### 1 `OAuth2`身份认证+鉴权

`initOauth2ClientCredentials`方法可以实现对token的自动续约与管理，指定client_id与client_secret即可

### 2 同步到`csv`文件`SyncToCSV`

使用案例在`exampleSyncToCSV()`方法中，开发者仅需在`example_csv.py`文件中进行配置即可。仅需配置`api`参数，包括`url`、`pageSize`等，还需配置写入的文件名。

### 3 同步到数据模型`SyncToModel`

因为写入到`csv`文件中的数据都是字符串类型，为满足开发者需求，提供同步数据到Model的功能。使用案例在`exampleSyncToModel()`方法中，开发者仅需在`example_model.py`文件中进行配置即可。配置：`Model`类型，`api`，指定`Model`对象

### 4 同步到数据库`SyncToDB`

使用案例在`exampleSyncToDB()`方法中，开发者仅需在`example_db.py`文件中进行配置即可。`ORM：sqlalchemy`

该`sdk`提供全量与增量刷新数据到DB中，支持数据库`MySQL`（建议）、`Oracle`、`PostgrelSQL`、`SQLServer`

目前暂时不支持 `upsert`，全量刷新时建议删除原本存在的表结构，增量同步时则不需要。配置如下：数据库、`api`、映射类，注意若接口返回的数据存在id，一般无需指定自增

