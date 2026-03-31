from dotenv import load_dotenv
from pathlib import Path
from langchain.tools import tool
from app.ai.schema.mysql_schema import MySqlSchema
from app.utils.Logger import Logger
import pymysql
import os


# 加载环境变量
env_path = Path(__file__).parent.parent / "analy.env"
load_dotenv(env_path)

# 创建日志记录器
logger = Logger.get_logger(__name__)

# 定义工具
@tool("mysql_tool", args_schema=MySqlSchema)
def mysql_tool(sql:str) -> str:
    """
    执行mysql语句
    数据库模式：
    user_info 用户信息表，字段：id,user_name,email
    customer 表
        字段：
            user_id(用户ID) - BIGINT, 主键
            username(用户名) - TEXT
            registration_date(注册日期) - TEXT/DATE
            country(国家) - TEXT
            age(年龄) - BIGINT
            gender(性别) - TEXT
            total_spent(总消费金额) - DOUBLE
            order_count(订单数量) - BIGINT
    products 表
        字段：
            product_id(产品ID) - BIGINT, 主键
            product_name(产品名称) - TEXT
            category(产品类别) - TEXT
            price(价格) - DOUBLE
            stock(库存) - BIGINT
            sales_volume(销售量) - BIGINT
            average_rating(平均评分) - DOUBLE
    orders 表
        字段：
            order_id(订单ID) - BIGINT, 主键
            user_id(用户ID) - BIGINT, 外键(users.user_id)
            order_date(订单日期) - TEXT/DATE
            product_id(产品ID) - BIGINT, 外键(products.product_id)
            quantity(数量) - BIGINT
            total_amount(总金额) - DOUBLE
            payment_method(支付方式) - TEXT
            order_status(订单状态) - TEXT
    customer_behavior 表
        字段：
            id(行为记录ID) - BIGINT, 主键
            user_id(用户ID) - BIGINT, 外键(users.user_id)
            product_id(产品ID) - BIGINT, 外键(products.product_id)
            action(行为类型) - TEXT (浏览/收藏/购买)
            action_date(行为日期) - TEXT/DATE
            device(设备类型) - TEXT
    sales 表
        字段：
            id(统计记录ID) - BIGINT, 主键
            year(年份月份) - TEXT (格式: YYYY-MM)
            total_sales(总销售额) - DOUBLE
            total_orders(总订单数) - BIGINT
            total_quantity_sold(总销售量) - BIGINT
            category(产品类别) - TEXT
            average_order_value(平均订单价值) - DOUBLE

    """
    try:
        # 连接数据库
        conn = pymysql.connect(
            host='localhost', 
            port=3306,
            user=os.getenv("MYSQL_USER"), 
            password=os.getenv("MYSQL_PASSWORD"), 
            db='analysis_agent'
        )
        # 创建游标
        cursor = conn.cursor()
        # 执行SQL语句
        rowcount = cursor.execute(sql)
        
        # 获取查询结果
        result = cursor.fetchall()
        
        # 获取SQL命令类型
        sql_command = sql.strip().upper().split()[0] if sql.strip() else ""
        
        # 获取最后插入的ID（仅对INSERT语句有效）
        lastrowid = cursor.lastrowid
        
        # 提交事务
        conn.commit()
        
        # 关闭游标
        cursor.close()
        # 关闭连接
        conn.close()

        # 返回查询结果
        if result:
            logger.info(f"SQL查询成功：{result}")
            return str(result)
        else:
            if sql_command in ('INSERT', 'UPDATE', 'DELETE'):
                if sql_command == 'INSERT':
                    return f"执行成功，影响了{rowcount}行，最后插入的ID为{lastrowid}"
                else:
                    return f"执行成功，影响了{rowcount}行"
            else:
                return "SQL语句执行成功，但没有返回结果"
    except Exception as e:
        logger.warning("执行SQL查询时出错:", e)
        return f"执行SQL查询时出错: {e}"
