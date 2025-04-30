import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text

def update_model(ip):
    try:
        # 创建 SQLAlchemy 引擎
        engine = create_engine(
            "mysql+mysqlconnector://szai:agent1234@localhost:30015/aiplat"
        )
        
        # 从数据库中拉取数据
        query_crawl = """
        SELECT * FROM (
            SELECT a.model_id, a.context_length, 2 as provider, b.desc, b.img_url 
            FROM (SELECT *
					FROM (
						SELECT 
							*,
							ROW_NUMBER() OVER (PARTITION BY model_name,area ORDER BY aiplat.volcengine_models.index) AS rn
						FROM aiplat.volcengine_models
					) AS ranked
					WHERE rn = 1
            ) a 
            INNER JOIN aiplat.volcengine_desc b 
            ON LOWER(a.model_name) = LOWER(b.model_id)
            UNION
            SELECT model_id, context_length, 1 as provider, aiplat.silicon_desc.desc, img_url 
            FROM aiplat.silicon_desc
        ) A;
        """
        df_crawl = pd.read_sql(query_crawl, con=engine)
        update_engine = create_engine(
            f"mysql+mysqlconnector://szai:agent1234@{ip}:30015/aiplat"
        )
        # 使用连接对象执行查询
        with update_engine.connect() as connection:
            for _, row in df_crawl.iterrows():
                model_id = row['model_id']
                provider = row['provider']
                desc = row['desc']
                img_url = row['img_url']
                context_length = row['context_length']
                desc = desc[:255] if desc else None

                # 查询是否存在相同的 model_id 和 provider
                query_check = text("""
                SELECT COUNT(*) FROM aiplat.custommodel_model
                WHERE name = :model_id AND provider_id = :provider;
                """)
                result = connection.execute(query_check, {"model_id": model_id, "provider": provider}).scalar()

                if result > 0:
                    # 如果存在，更新字段
                    query_update = text("""
                    UPDATE aiplat.custommodel_model
                    SET `desc` = :desc, img_url = :img_url, context_length = :context_length, 
                    updated_at = sysdate(),status = 2,price=0.01
                    WHERE BINARY name = :model_id AND provider_id = :provider;
                    """)
                    rows_updated = connection.execute(query_update, {
                        "desc": desc,
                        "img_url": img_url,
                        "context_length": context_length,
                        "model_id": model_id,
                        "provider": provider
                    }).rowcount

                    if rows_updated == 0:
                        print(f"No rows updated for model_id: {model_id}, provider: {provider}. Check your data.")
                else:
                    # 如果不存在，插入新的一行
                    query_insert = text("""
                    INSERT INTO `aiplat`.`custommodel_model`
                    (`name`,`cate`,`price`,`desc`,`context_length`,`provider_id`,`status`,`user_id`,`img_url`,created_at,updated_at,priority)
                    VALUES (:model_id, 'text', 0.01, :desc, :context_length, :provider, 2, 1, :img_url, sysdate(), sysdate(),0);
                    """)
                    connection.execute(query_insert, {
                        "model_id": model_id,
                        "desc": desc,
                        "context_length": context_length,
                        "provider": provider,
                        "img_url": img_url
                    })
            

                print(f"Processed model_id: {model_id}, provider: {provider}")
             # 如果没更新到说明下架了
            query_update = text("""
            update aiplat.custommodel_model set status=1 where updated_at < NOW() - INTERVAL 1 HOUR
            """)
            connection.execute(query_update)

            query_update = text("""
            update aiplat.custommodel_model 
            set status=1
            where name in ('deepseek-v3-241226','240828')
            """)
            connection.execute(query_update)
            
            connection.commit()

    except Exception as e:
        print(f"Error updating database: {e}")
    finally:
        # 关闭数据库连接
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    # 更新数据库
    update_model("localhost")
    # update_model("20.2.137.144")
    # update_model("57.158.24.38")