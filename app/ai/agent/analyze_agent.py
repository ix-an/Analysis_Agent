from dotenv import load_dotenv
from pathlib import Path
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver  # 同步PostgresSQL记忆
from app.utils.Logger import Logger
from app.utils.model import QwenModel
from app.ai.tool.mysql_tool import mysql_tool
from app.utils.permission_middle import before_agent_middleware
from app.ai.schema.analyze_response import AnalyzeResponse
import os

load_dotenv(Path(__file__).parent.parent.parent / "analy.env")
logger = Logger.get_logger(__name__)

"""
数据分析智能体
"""
class AnalyzeAgent:
    def __init__(self):
        self.model = QwenModel().model
        self.tools = self.init_tools()
        logger.info("初始化数据分析智能体")

    # 创建工具
    def init_tools(self):
        self.tools = [mysql_tool]
        return self.tools

    def answer(self, question: str, user_id: int | str):
        # 提示词
        prompt = """
        一：你是一个数据分析助手，你有一个工具：mysql_tool
        二：工作流程：你必须严格按照以下步骤来执行
            步骤一: 查询数据，把数据以表格形式存入到表格数据
            步骤二: 根据问题做出数据分析，按照以下格式来分析，把分析结果存入到分析结果
                 一：详细分析
                    1 xxxx:
                        xxxx
                        xxxx
                    2 xxxx:
                        xxxx
                        xxxx
                 二：结论部分：
                     .xxxxx
                     .xxxxx
                     .xxxxx
            步骤三：生成一个echarts图表，图表数据json格式必须是以下要求，把数据存入到图表数据
                1 返回的数据必须是一个可执行的json格式，其它的文本信息不需要
                2 返回的图表必须有保存功能 
        三：重要规则
                1. **SQL生成规范**:
                    - 只能使用SELECT查询，禁止使用INSERT/UPDATE/DELETE等修改操作
                2. **查询原则**:
                    - 涉及排名或TOP N时，必须使用ORDER BY和LIMIT
                    - 多表查询时使用正确的JOIN关系
                    - 只查询前5条记录
        """

        # 构建消息对象
        msg = HumanMessage(content=question, user_id=user_id)

        # -----连接postgres数据库 -----
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
            a_agent = create_agent(
                model=self.model,
                tools=self.tools,
                system_prompt=prompt,
                debug=False,
                checkpointer=pg,
                response_format=AnalyzeResponse,
                middleware=[before_agent_middleware]  # 权限中间件
            )
            # 执行智能体
            try:
                res = a_agent.invoke(
                    {"messages": [msg]},
                    {"configurable": {"thread_id": user_id}}
                )
                # 返回格式化的数据
                data = res["structured_response"].model_dump()
                logger.info(f"数据分析接口返回数据：{data}")
                return data
            except Exception as e:
                logger.error(f"数据分析接口发生错误：{e}")
                return e


if __name__ == '__main__':
    agent = AnalyzeAgent()
    print(agent.answer("2023年3月份销售情况数据分析", "xx@qq.com"))


