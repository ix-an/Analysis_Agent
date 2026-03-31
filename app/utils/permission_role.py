"""
验证用户角色权限：查询角色
"""
from app.utils.Logger import Logger
from dotenv import load_dotenv
from pathlib import Path
import os
import pymysql

logger = Logger.get_logger(__name__)
load_dotenv(Path(__file__).parent.parent.parent / "analy.env")

def permission_role(user_id:str) -> str | None:
    # 定义sql语句，查询用户角色
    sql = f"select role from user_info where email ='{user_id}'"
    # 创建链接
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        db='analysis_agent'
    )
    # 创建游标
    cursor = conn.cursor()
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 获取结果
        result = cursor.fetchall()
        if len(result) > 0:
            logger.info(f"角色：{result[0][0]}")
            return result[0][0]
        else:
            logger.warning(f"用户不存在：{user_id}")
            return  None
    except Exception as e:
        logger.error(f"查询用户角色失败：{e}")
        return None
    finally:
        cursor.close()  # 关闭游标
        conn.close()  # 关闭连接


if __name__ == '__main__':
    rs = permission_role("xx@qq.com")
    print(rs)
