from dotenv import load_dotenv
from pathlib import Path
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver  # 异步PostgresSQL记忆
from app.utils.Logger import Logger
from app.utils.model import QwenModel
from app.ai.tool.mysql_tool import mysql_tool
from app.utils.permission_middle import before_agent_middleware
import asyncio
import os

load_dotenv(Path(__file__).parent.parent.parent / "analy.env")
# 创建日志记录器
logger = Logger.get_logger(__name__)

"""
SQL问答智能体：PostgresSQL记忆
"""
class SqlAgentPg:
    def __init__(self):
        logger.info("初始化sql问答助手智能体：PostgresSQL记忆")
        self.model = QwenModel().model
        self.tools = self.init_tools()


    # 初始化工具
    def init_tools(self):
        self.tools =[mysql_tool]
        return self.tools

    # 执行问答智能体：异步
    async def answer(self, question: str, user_id: int | str):
        """
        在这里创建智能体
        """
        # 提示词
        prompt = """
        一：你是一个sql问答助手，你有一个工具：mysql_tool
        二：重要规则：
        - 只能使用select查询，禁止使用INSERT/UPDATE/DELETE等修改操作
        三：使用规则：
        - 如果查询销售数据，请查询sales
        - 涉及排名或TOP N时，必须使用ORDER BY和LIMIT
        - 多表查询时使用正确的JOIN关系
        """

        # 创建数据库链接
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST")
        db = os.getenv("POSTGRES_DB")
        url = f"postgresql://{user}:{password}@{host}:5432/{db}?sslmode=disable"

        # 创建智能体，使用 AsyncPostgresSaver异步来处理流式输出
        async with AsyncPostgresSaver.from_conn_string(url) as pg:
            # 安装数据库和表
            await pg.setup()
            # 创建智能体
            pg_agent = create_agent(
                model=self.model,
                tools=self.tools,
                system_prompt=prompt,
                debug=False,
                checkpointer=pg,
                middleware=[before_agent_middleware]
            )
            # 创建消息对象
            msg = HumanMessage(content=question, user_id=user_id)
            try:
                # 执行智能体
                res = pg_agent.astream(
                    {"messages": [msg]},
                    {"configurable": {"thread_id": user_id}},
                    stream_mode="messages"
                )
                # 遍历输出
                async for chunk, _ in res:
                    # 不返回工具调用信息，只返回答案信息
                    if not hasattr(chunk, "tool_call_id"):
                        yield chunk.content
            except Exception as e:
                logger.error(f"聊天接口发生错误：{e}")
                yield e


if __name__ == '__main__':
    import asyncio
    import sys
    # 在 Windows 系统上设置 SelectorEventLoop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    agent = SqlAgentPg()
    # 定义生成器函数
    async def main():
        async for chunk in agent.answer("李四的年龄是？", 1):
            print(chunk, end="")

    asyncio.run(main())
