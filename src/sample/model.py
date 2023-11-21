import json
import requests
from src.sample.oauth_init import GetOpenAPIClient

class APIResult:
    def __init__(self, err_code, err_msg, request_id, data):
        self.errCode = err_code
        self.errMsg = err_msg
        self.requestId = request_id
        self.data = data

def ParseApiResult(response, debug=False):
    data = APIResult(0, '', '', None)
    if debug:
        print(response.url)
        print(response.status_code)
        print(response.headers)

    if response.status_code != 200:
        if response.headers.get("X-Ca-Error-Code") == "A401OT":
            return data, Exception("A401OT")

        return data, Exception("invoke api get fail, X-Ca-Error-Code: {}, X-Ca-Error-Message: {}, X-Ca-Request-Id: {}".format(
            response.headers.get("X-Ca-Error-Code"),
            response.headers.get("X-Ca-Error-Message"),
            response.headers.get("X-Ca-Request-Id")
        ))

    if response.content is None:
        return data, Exception("get api response body is None")

    if debug:
        print(response.text)

    try:
        data.errCode = json.loads(response.text).get('errCode')
        data.errMsg = json.loads(response.text).get('errMsg')
        data.requestId = json.loads(response.text).get('requestId')
        data.data = json.loads(response.text).get('data')
    except Exception as e:
        return data, Exception("parse getapi response body fail: {}".format(str(e)))

    return data, None

# 同样http请求
def HttpRequest(url, method, data=None):
    # 获取token
    c = GetOpenAPIClient()
    token = c.getAccessToken()
    headers = {"Authorization": "Bearer " + token}

    # 根据请求方法选择合适的请求函数
    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, data=data, headers=headers)
    elif method == 'PUT':
        response = requests.put(url, data=data, headers=headers)
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError('Unsupported HTTP method')
    return response

# 通用get请求
def HttpGet(url):
    try:
        response = HttpRequest(url, 'GET')
    except Exception as e:
        return None, Exception("invoke api get fail: {}".format(str(e)))

    c = GetOpenAPIClient()
    apiResult, err = ParseApiResult(response, c.debug)

    if err != None:
        if err == "A401OT" and c.RetryCount <= 3 :
            c.retryAdd()
            return HttpGet(url, 'GET')
        return None, err
    
    if c.RetryCount > 0 :
        c.retryReset()

    if apiResult.errCode != 0 :
        return None, Exception(apiResult.errMsg)

    return apiResult.data, None

def callAPI(url, method):
    if method == "GET":
        response = HttpGet(url)
    return response
