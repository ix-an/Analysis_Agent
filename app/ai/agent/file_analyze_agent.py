from langchain.agents import create_agent
from pathlib import Path
from app.utils.Logger import Logger
from app.utils.model import QwenModel
from app.utils.file_reader import file_reader_tool
from app.utils.file_writer import docx_write_tool
from langchain_core.prompts import PromptTemplate
import os

logger = Logger.get_logger(__name__)

"""
文件数据分析智能体：传入文件，根据用户意图，生成分析报告
"""
class FileAnalyzeAgent:
    def __init__(self):
        logger.info("初始化文件数据分析智能体")
        self.model = QwenModel().model
        self.tools = self.init_tools()

    def init_tools(self):
        self.tools = [file_reader_tool,docx_write_tool]
        return self.tools

    # 创建智能体：异步，不需要记忆
    async def answer(self,question:str,user_id:str):
        # 提示词
        prompt = """
        你是一个专业的【销售数据分析与战略顾问】。
        当前用户上传了一个文件，路径为：{path}

        你的工作流程如下，请严格执行：
        1. **读取与清洗**：调用 `file_reader_tool` 获取已初步清洗的文件内容。
        2. **深度分析**：基于文件中的数据或文字，撰写一份“销售指导分析报告”。
           报告必须包含：
           - 数据概况总结。
           - 销售痛点分析（如果数据中体现了波动或异常）。
           - 【核心】具体的销售指导建议：给出至少 3 条可落地的销售话术或渠道优化方案。
        3. **生成报告**：将上述完整的“销售指导分析报告”内容调用 `docx_write_tool` 写入新文档。
        4. **结果交付**：直接向用户展示你的简要分析结论，并贴出 `docx_write_tool` 返回的【下载链接】。

        注意：不要问用户该怎么做，请直接开始分析并生成下载链接。
        """
        # 项目根目录
        base_dir = Path(__file__).resolve().parent.parent.parent
        # 上传目录路径
        upload_dir = base_dir / "static/upload"
        # 获取文件路径
        path = os.path.join(upload_dir,question.split(":")[1])
        logger.info(f"文件路径为：{path}")
        # 提示词模板化
        prompt_temple = PromptTemplate.from_template(prompt)
        # 填充path到提示词
        prompt = prompt_temple.format(path=path)

        # 创建智能体
        agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=prompt,
        )

        # 遍历生成器
        async for chunk, _ in agent.astream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="messages"
        ):
            # 只返回内容，不返回工具调用信息
            if not hasattr(chunk, "tool_call_id"):
                yield chunk.content


if __name__ == "__main__":
    import asyncio
    agent = FileAnalyzeAgent()
    async def main():
        async for c in agent.answer("上传文件:test.docx","xx@qq.com"):
            print(c, end="")
    asyncio.run(main())
