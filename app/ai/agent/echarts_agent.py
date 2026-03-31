from dotenv import load_dotenv
from pathlib import Path
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver  # 同步PostgresSQL记忆
from app.utils.Logger import Logger
from app.utils.model import QwenModel
from app.ai.tool.mysql_tool import mysql_tool
from app.utils.permission_middle import before_agent_middleware
from app.ai.schema.echarts_response import EchartsResponse
import os

load_dotenv(Path(__file__).parent.parent.parent / "analy.env")
logger = Logger.get_logger(__name__)

"""
Echarts图表生成智能体
"""
class EchartsAgent:
    def __init__(self):
        logger.info("初始化Echarts图表生成智能体")
        self.model = QwenModel().model
        self.tools = self.init_tools()

    # 创建工具
    def init_tools(self):
        self.tools = [mysql_tool]
        return self.tools

    # 执行Echarts图表生成智能体
    def answer(self, question: str, user_id: int | str):
        # 提示词
        prompt = """
        一 ：你是一个echarts图表生成助手，你有一个工具 mysql_tool
        二：工作流程：请严格按照下面格式回答问题
            1 如果用户问图表生成，请先查询数据库，生成一个echarts图表，图表数据json格式必须是以下要求
            2 返回的数据必须是一个可执行的json格式，其它的文本信息不需要
            3 返回的图表必须有保存功能  
        三：重要规则
            1. **SQL生成规范**:
                - 只能使用SELECT查询，禁止使用INSERT/UPDATE/DELETE等修改操作
            2. **查询原则**:
                - 涉及排名或TOP N时，必须使用ORDER BY和LIMIT
                - 多表查询时使用正确的JOIN关系
                - 只查询前10条记录
        四：反馈信息
            1 如果返回的json数据， 请返回状态码200，提示信息是；生成成功
            2 如果返回的json数据， 请返回状态码500，提示信息是；生成失败
        """
        # 构建消息对象
        msg = HumanMessage(content=question, user_id=user_id)

        # ----- 创建链接，读取数据库信息 -----
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST")
        db = os.getenv("POSTGRES_DB")
        url = f"postgresql://{user}:{password}@{host}:5432/{db}?sslmode=disable"

        # 创建智能体：PostgresSQL记忆
        with PostgresSaver.from_conn_string(url) as pg:
            # 安装数据库和表
            pg.setup()
            # 创建智能体
            e_agent = create_agent(
                model=self.model,
                tools=self.tools,
                system_prompt=prompt,
                debug=False,
                checkpointer=pg,
                response_format=EchartsResponse,
                middleware=[before_agent_middleware]
            )
            try:
                res = e_agent.invoke(
                    {"messages": [msg]},
                    {"configurable": {"thread_id": user_id}}
                )
                # 返回格式化的数据
                data = res["structured_response"].model_dump()
                logger.info(f"Echarts图表生成接口返回数据：{data}")
                return data
            except Exception as e:
                logger.error(f"Echarts图表生成接口发生错误：{e}")
                return e


if __name__ == '__main__':
    agent = EchartsAgent()
    print(agent.answer("2023年1月份的销售数据，请用柱状图图表分析一下", "xx@qq.com"))
