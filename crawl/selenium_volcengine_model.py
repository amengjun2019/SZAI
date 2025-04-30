from time import sleep
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import glob
from sqlalchemy import create_engine
# import mysql.connector

def scrape_models_with_selenium(url, username, password):
    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器界面
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")

    # 指定 ChromeDriver 路径
    driver_path = "chromedriver-mac-arm64/chromedriver"  # 替换为你的 ChromeDriver 路径
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 打开登录页面
        driver.get("https://console.volcengine.com/auth/login/")

        # 等待登录页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Identity_input"))
        )

        # 输入用户名
        username_input = driver.find_element(By.ID, "Identity_input")
        username_input.send_keys(username)

        # 输入密码
        password_input = driver.find_element(By.ID, "Password_input")
        password_input.send_keys(password)

        # 点击登录按钮
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        driver.set_page_load_timeout(60)
        # 打开目标页面
        # driver.get(url)
        # sleep(5)
        for attempt in range(3):  # 尝试 3 次
            try:
                driver.get(url)
                WebDriverWait(driver, 60).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.volc-viewer-table"))
            )
                break  # 如果成功加载页面，退出循环
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 2:  # 如果最后一次尝试仍失败，抛出异常
                    raise
        # 获取页面内容
        tables = driver.find_elements(By.CSS_SELECTOR, "table.volc-viewer-table") # 替换为实际的 HTML 结构

        if not tables:
            print("No models found on the page.")
            return
        
        for i in range(len(tables)):
            table=tables[i]
            # 查找当前 table 标签前一个 p 标签中的内容
            previous_p = table.find_element(By.XPATH, "preceding-sibling::p[1]")
            if "文本生成" not in previous_p.text and "深度思考" not in previous_p.text:
                continue
             # 提取表头
            headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]
            
            # 提取行数据
            data = []
            for row in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
                # 处理特殊单元格结构（如包含代码块）
                cells = row.find_elements(By.TAG_NAME, "td")
                row_data = []
                for cell in cells:
                    # 处理可能存在的嵌套元素
                    # if cell.find_elements(By.TAG_NAME, "code"):
                    #     content = "|".join([code.text for code in cell.find_elements(By.TAG_NAME, "code")])
                    # else:
                    content = cell.text.strip().replace('\n', ' ')
                    row_data.append(content)
                if len(data)>0 and len(row_data)<len(data[len(data)-1]):
                    row_data.insert(0,data[len(data)-1][0])
                data.append(row_data)

            # 保存数据
            with open('csvdata/volc_table{}.csv'.format(i), 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)

    finally:
        # 关闭浏览器
        driver.quit()

def update_database_from_csv(csv_file_pattern, table_name):

    try:
         # 拼接多个 CSV 文件
        csv_files = glob.glob(csv_file_pattern)
        dataframes = []

        for file in csv_files:
            df = pd.read_csv(file)
            
            # 去除 df 列名中的特殊字符和换行符，括弧不去除
            df.columns = [col.replace('\r\n', '').replace('\n', '').replace('（', '(').replace('）', ')').strip() for col in df.columns]
            columns_to_keep = ['模型 ID(Model ID)']
            if all(col in df.columns for col in columns_to_keep):
                columns_to_keep = ['模型名称','版本','模型 ID(Model ID)', '模型领域', '模型能力','最大上下文长度(token)']
                columns_to_keep = [col for col in columns_to_keep if col in df.columns]
                df = df[columns_to_keep]
                df['index'] = df.index
                df['模型 ID(Model ID)'] = df.apply(
                    lambda row: row['模型名称'] + "-"+ str(row['模型 ID(Model ID)']) if len(str(row['模型 ID(Model ID)'])) < 7 else row['模型 ID(Model ID)'],
                    axis=1
                )
            else:
                continue
            dataframes.append(df)

        # 合并所有 DataFrame，表头不一致时填充空值
        combined_df = pd.concat(dataframes, ignore_index=True, sort=False)
        # 填充模型领域为空的字段
        combined_df['模型领域'] = combined_df.apply(
            lambda row: row['模型能力'] if pd.isna(row['模型领域']) or row['模型领域'] == '' else row['模型领域'], axis=1
        )
        combined_df= combined_df[['模型名称','版本','模型 ID(Model ID)', '模型领域', '最大上下文长度(token)','index']]
        # 重命名列名
        combined_df.rename(columns={
            '模型名称': 'model_name','版本': 'version',
            '模型 ID(Model ID)': 'model_id_web',
            '模型领域': 'area',
            '最大上下文长度(token)': 'context_length'
        }, inplace=True)
        combined_df['provider'] = 'volcengine'
        combined_df['model_id'] = combined_df['model_id_web'].apply(lambda x: x.split(' ')[0])
  
        # 创建 SQLAlchemy 引擎
        engine = create_engine(
            "mysql+mysqlconnector://szai:agent1234@localhost:30015/aiplat"
        )

        # 将 DataFrame 存入 MySQL 数据库
        combined_df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        
    except Exception as e:
        print(f"Error updating database: {e}")
    finally:
        # 关闭数据库连接
        if 'engine' in locals():
            engine.dispose()
        


if __name__ == "__main__":
    url = "https://www.volcengine.com/docs/82379/1330310"
    username ="5778手机用户#AzJjBP" # 替换为你的用户名
    password = "leon123456@"  # 替换为你的密码
    # scrape_models_with_selenium(url, username, password)
    # 更新数据库
    update_database_from_csv("csvdata/volc_table*.csv", "volcengine_models")
  
