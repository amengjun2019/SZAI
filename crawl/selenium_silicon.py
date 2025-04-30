from time import sleep
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def scrape_model_details(url):
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
        # # # 配置Selenium
        # driver.get("https://account.siliconflow.cn/zh/login")

        # # 点击第三方登录按钮
        # third_party_login_btns = WebDriverWait(driver, 10).until(
        #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.ant-btn-icon-only"))
        # )
        # driver.find_element(By.ID, "agree").click()
        # third_party_login_btns[1].click()
        # sleep(5)  # 等待页面加载

        # print(driver.current_url)

        # github_login_btn = WebDriverWait(driver, 300).until(
        #     EC.element_to_be_clickable((By.NAME, "commit"))
        # )

        # # 切换窗口并输入账号（注意：可能违反第三方服务条款）
        # # driver.switch_to.window(driver.window_handles[1])
        # email_input = driver.find_element(By.ID, "login_field")
        # email_input.send_keys("amengjun@126.com")
        # password_input = driver.find_element(By.ID, "password")
        # password_input.send_keys("Mj719907@")
        # # driver.find_element(By.NAME, "commit").click()
        # github_login_btn.click()

        driver.set_page_load_timeout(60)
        # 打开目标页面
        for attempt in range(3):  # 尝试 3 次
            try:
                driver.get(url)
                 # 等待页面加载完成
                WebDriverWait(driver, 60).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.border.border-transparent.cursor-pointer"))
                )
                break  # 如果成功加载页面，退出循环
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 2:  # 如果最后一次尝试仍失败，抛出异常
                    raise
        # 增加调试信息
        print("Waiting for elements to load...")
      
        model_cards = [
            card for card in driver.find_elements(By.CSS_SELECTOR, "div.border.border-transparent.cursor-pointer")
            if "hover:border-transparent" not in card.get_attribute("class")
        ]

        # 打开 CSV 文件以写入数据
        with open("csvdata/silicon_desc.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # 写入表头
            writer.writerow(["model_id", "desc","context_length", "img_url"])

            # 遍历每个模型卡片并提取数据
    
            for card in model_cards:
                try:
                    # 提取模型名称
                    name_element = card.find_element(By.CSS_SELECTOR, "div.w-full.truncate.text-base")
                    model_name = name_element.text.strip()
                    # 提取模型图片链接
                    img_element = card.find_element(By.CSS_SELECTOR, "img")
                    img_src = img_element.get_attribute("src")
                    # 提取模型描述
                    desc_element = card.find_element(By.CSS_SELECTOR, "div.ant-typography")
                    model_description = desc_element.text.strip()

                     # 提取模型上下文长度
                    tags=card.find_elements(By.CSS_SELECTOR, "div.text-primary")
                    for tag in tags:
                        if "K" in tag.text:
                            context_element = tag
                            break
                    # context_element = card.find_element(By.CSS_SELECTOR, "div.flex.gap-2.truncate")
                    context_length = context_element.text.strip()


                    # 写入 CSV 文件
                    writer.writerow([model_name, model_description,context_length,img_src])

                except Exception as e:
                    print(f"Error extracting data for a card: {e}")

    finally:
        # 关闭浏览器
        driver.quit()

if __name__ == "__main__":
    scrape_model_details("https://cloud.siliconflow.cn/open/models?types=chat")
