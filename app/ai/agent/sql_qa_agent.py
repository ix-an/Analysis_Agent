from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  # 内存级记忆（测试用）
from app.utils.Logger import Logger
from app.utils.model import QwenModel
from app.ai.tool.mysql_tool import mysql_tool
import asyncio

# 创建日志记录器
logger = Logger.get_logger(__name__)

"""
SQL问答智能体
"""
class SqlAgent:
    def __init__(self):
        logger.info("初始化sql问答助手智能体")
        self.model = QwenModel().model
        self.tools = self.init_tools()
        self.agent = self.init_agent()


    # 初始化工具
    def init_tools(self):
        self.tools =[mysql_tool]
        return self.tools

    # 创建智能体
    def init_agent(self):
        # 提示词
        prompt = """
        你是一个sql问答助手，你有一个工具：mysql_tool 
        """
        # 创建智能体
        sql_qa_agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=prompt,
            debug=False,
            checkpointer=InMemorySaver()
        )
        return sql_qa_agent

    # 执行问答智能体：异步
    async def answer(self, question: str, user_id: int | str):
        res = self.agent.astream(
            {"messages" :[{"role":"user","content":question}]},
            {"configurable": {"thread_id": user_id}},
            stream_mode="messages"
        )
        async for chunk, _ in res:
            # 不返回工具调用信息，只返回答案信息
            if not hasattr(chunk,"tool_call_id"):
                yield chunk.content



if __name__ == '__main__':
    agent = SqlAgent()
    # 定义生成器函数
    async def main():
        async for chunk in agent.answer("李四的年龄是？", 1):
            print(chunk, end="")

    asyncio.run(main())
