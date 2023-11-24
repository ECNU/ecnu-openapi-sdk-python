from ecnuopenapi.oauth_init import GetOpenAPIClient
from ecnuopenapi.model import HttpGet

class DataResult:
    def __init__(self, PageSize=0, PageNum=0, Rows=[]):
        self.PageSize = PageSize
        self.PageNum = PageNum
        self.Rows = Rows

def getRows(apiPath, pageNum, pageSize):
    dataResult = DataResult()
    c = GetOpenAPIClient()
    if '?' in apiPath :
        url = f"{c.base_url}{apiPath}&pageNum={pageNum}&pageSize={pageSize}"
    else:
        url = f"{c.base_url}{apiPath}?pageNum={pageNum}&pageSize={pageSize}"
    data, err = HttpGet(url)
    if err != None:
        return dataResult, err
    try:
        dataResult.Rows = data['rows']
    except Exception as e:
        return dataResult, Exception(str(e))

    return dataResult, err

def getAllRows(apiPath, pageSize):
    rows = []
    pageNum = 1
    while True:
        result, err = getRows(apiPath, pageNum, pageSize)
        if err != None:
            return rows, err
        if len(result.Rows) == 0:
            break
        pageNum += 1
        rows.extend(result.Rows)
    return rows, None
