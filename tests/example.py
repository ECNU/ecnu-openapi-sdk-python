import sys
import os

current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

from src.sample.oauth_init import OAuth2Config, initOauth2ClientCredentials
from src.sample.model import callAPI
from example_csv import exampleSyncToCSV
from example_model import exampleSyncToModel
from example_db import exampleSyncToDB
from example_performance import exampleSyncPerformance


if __name__ == "__main__":
    config = OAuth2Config(
        client_id="",
        client_secret="",
    )
    initOauth2ClientCredentials(config)
    print(callAPI('https://api.ecnu.edu.cn/api/v1/sync/fakewithts?ts=0&pageSize=1&pageNum=1', 'GET'))
    exampleSyncToCSV()
    exampleSyncToModel()
    exampleSyncToDB()
    exampleSyncPerformance()

