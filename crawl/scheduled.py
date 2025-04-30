from selenium_silicon import scrape_model_details as scrape_silicon
from selenium_volcengine_model import scrape_models_with_selenium as scrape_volcengine
from selenium_volcengine_model import update_database_from_csv as update_volcengine
from update_db import update_database_from_csv as update_silicon
from update_models import update_model
import os
import glob

if __name__ == "__main__":
    files = glob.glob("csvdata/*")
    for file in files:
        os.remove(file)
    scrape_silicon("https://cloud.siliconflow.cn/open/models?types=chat")
    username ="5778手机用户#AzJjBP" # 替换为你的用户名
    password = "leon123456@"  # 替换为你的密码
    scrape_volcengine("https://www.volcengine.com/docs/82379/1330310", username, password)
    # update_volcengine("csvdata/volc_table*.csv", "volcengine_models")
    # update_silicon("csvdata/silicon_desc.csv", "silicon_desc", "silicon")
    # update_model("172.16.110.228")
    # Delete all files in the csvdata folder

    # update_model("20.2.137.144")
    # update_model("57.158.24.38")
    files = glob.glob("csvdata/*")
    for file in files:
        os.remove(file)