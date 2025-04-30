# 爬虫项目

本项目是一个基于 Selenium 和 BeautifulSoup 的爬虫工具，用于从多个网站（如 SiliconFlow 和 VolcEngine）抓取模型数据，并将其存储到 MySQL 数据库中。

---

## 功能

1. **爬取 SiliconFlow 模型数据**：
   - 从 `https://cloud.siliconflow.cn/open/models?types=chat` 页面抓取模型的详细信息。

2. **爬取 VolcEngine 模型数据**：
   - 从 `https://www.volcengine.com/docs/82379/1330310` 页面抓取模型的详细信息。

3. **清理 CSV 数据**：
   - 自动清理 `csvdata` 文件夹中的旧数据。

4. **更新 MySQL 数据库**：
   - 将抓取的数据存储到 MySQL 数据库中。

---

## 项目结构

GitHub Copilot
以下是生成的 README.md 文件内容：

project/ 
  ├── csvdata/ # 存放爬取的 CSV 数据 
  ├── scheduled.py # 主脚本，调度爬虫任务 
  ├── selenium_silicon.py # 爬取 SiliconFlow 的脚本 
  ├── selenium_volcengine_model.py # 爬取 VolcEngine 的脚本 
  ├── update_db.py # 更新数据库的脚本 
  ├── update_models.py # 更新模型的脚本 
  ├── requirements.txt # Python 依赖文件 
  ├── Dockerfile # Dockerfile 文件 
  ├── docker-compose.yml # Docker Compose 文件 
  └── README.md # 项目说明文件


---

## 环境要求

- Python 3.12.2
- MySQL 数据库

---

## 安装与运行

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/crawl.git
cd crawl
```
### 2. 使用 pip 安装项目依赖
```bash
pip install -r [requirements.txt]
```
### 3. 配置 MySQL 数据库
确保你的 MySQL 数据库已启动，并在 selenium_volcengine_model.py 和其他脚本中正确配置了数据库连接信息：
```bash
engine = create_engine(
    "mysql+mysqlconnector://szai:agent1234@localhost:30015/aiplat"
)
```
# 配置文件说明
scheduled.py
主调度脚本，包含以下功能：
    清理 csvdata 文件夹中的旧数据。
    调用 scrape_silicon 和 scrape_volcengine 函数抓取数据。
    可选地调用 update_volcengine 和 update_silicon 函数更新数据库。
selenium_silicon.py
爬取 SiliconFlow 模型数据的脚本，抓取以下信息：

    模型名称
    描述
    上下文长度
    图片链接
selenium_volcengine_model.py

爬取 VolcEngine 模型数据的脚本，抓取以下信息：

    模型名称
    版本
    模型领域
    最大上下文长度
