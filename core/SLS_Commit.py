import time
import os
from aliyun.log import *

def sls_query(query):
    access_key_id = ""
    access_key = ''

    # Project 和 Logstore 名称
    project = ''
    # project = 'sls-alert-1060893066784074-cn-beijing'
    logstore = ''

    # 创建日志服务 Client
    endpoint = ''  # 根据实际地域选择合适的 endpoint
    client = LogClient(endpoint, access_key_id, access_key)

    # 设置查询时间范围，这里查询最近1小时的日志
    from_time = int(time.time()) - 36000
    to_time = int(time.time())

    # 设置返回日志条数和偏移量
    line = 100
    offset = 0

    # 构建 GetLogs 请求
    request = GetLogsRequest(project, logstore, from_time, to_time, '', query=query, line=line, offset=offset, reverse=False)

    # 执行查询
    response = client.get_logs(request)

    res = []
    for log in response.get_logs():
        res.append(log.contents.items())
    return res

if __name__ == '__main__':
    res = sls_query("request_method:GET AND request_length:612")
    print(res)