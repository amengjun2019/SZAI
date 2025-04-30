import pandas as pd
import glob
from sqlalchemy import create_engine
import mysql.connector

def update_database_from_csv(csv_file, table_name,provider):

    try:

        df = pd.read_csv(csv_file)
        columns_to_keep = ["model_id", "desc","context_length", "img_url","tags"]
        columns_to_keep = [col for col in columns_to_keep if col in df.columns]
        df = df[columns_to_keep]
        df['provider'] = provider 
        # 创建 SQLAlchemy 引擎
        engine = create_engine(
            "mysql+mysqlconnector://szai:agent1234@localhost:30015/aiplat"
        )
        # 将 DataFrame 存入 MySQL 数据库
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        
    except Exception as e:
        print(f"Error updating database: {e}")
    finally:
        # 关闭数据库连接
        if 'engine' in locals():
            engine.dispose()
      
if __name__ == "__main__":
    # 更新数据库
    update_database_from_csv("silicon_desc.csv", "silicon_desc", "silicon")
    # update_database_from_csv("volcengine_desc.csv", "volcengine_desc", "volcengine")