from time import sleep
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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
    

        # 打开目标页面
        driver.get(url)

        sleep(5)  # 等待页面加载

        # # 等待页面加载完成
        # WebDriverWait(driver, 30).until(
        #     EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'model-card-af5962')]"))  # 替换为实际的 HTML 结构
        # )

        # 获取页面内容
        models = driver.find_elements(By.CSS_SELECTOR, "div.model-card-af5962.not-preview-_31810") # 替换为实际的 HTML 结构

        if not models:
            print("No models found on the page.")
            return
        # 打开 CSV 文件以写入数据
        with open("volcengine_desc.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # 写入表头
            writer.writerow(["model_id","tags", "desc", "img_url"])

            # 遍历每个模型并提取数据
            for i in range(len(models)):
                model = models[i]  # 使用索引获取当前元素
                title_element = model.find_element(By.CLASS_NAME, "model-title-_54602")
                model_title = title_element.text.strip()

                tag_element = model.find_element(By.CLASS_NAME, "model-tags-a43660")
                model_tag = tag_element.text.strip()

                des_element = model.find_element(By.CLASS_NAME, "model-description-e9e21d")
                model_des = des_element.text.strip()

                img_element = model.find_element(By.CLASS_NAME, "model-icon-_1db92")
                model_img = img_element.get_attribute("srcset")  # 提取图片 URL
                writer.writerow([model_title,model_tag, model_des, model_img])

    finally:
        # 关闭浏览器
        driver.quit()
import mysql.connector
def update_database_from_csv(csv_file_path):
    # 连接 MySQL 数据库
    connection = mysql.connector.connect(
        host="57.158.24.38",  # 替换为你的数据库主机
        user="szai",       # 替换为你的数据库用户名
        password="agent1234",  # 替换为你的数据库密码
        database="aiplat",  # 替换为你的数据库名称
        port=30015,  # 替换为你的数据库端口
    )
    cursor = connection.cursor()

    try:
        # 打开 CSV 文件并读取数据
        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # 跳过表头

            for row in reader:
                model_title, model_tag, model_des, model_img = row

                # 更新数据库表字段
                update_query = """
                UPDATE aiplat.custommodel_model
                SET `desc` = %s, img_url = %s
                WHERE name like %s               
                """
                cursor.execute(update_query, ( model_des, model_img,  f"%{model_title}%"))

        # 提交更改
        connection.commit()
        print("Database updated successfully.")

    except Exception as e:
        print(f"Error updating database: {e}")
        connection.rollback()

    finally:
        # 关闭数据库连接
        cursor.close()
        connection.close()


   
if __name__ == "__main__":
    # update_database_from_csv("models_data.csv")
    url = "https://console.volcengine.com/ark/region:ark+cn-beijing/model?feature=&vendor=Bytedance&view=LIST_VIEW"
    username ="5778手机用户#AzJjBP" # 替换为你的用户名
    password = "leon123456@"  # 替换为你的密码
    scrape_models_with_selenium(url, username, password)