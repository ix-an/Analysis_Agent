"""
阿里云百炼大模型服务类封装
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pathlib import Path
import os

# 加载环境变量
env_path = Path(__file__).parent.parent.parent / "analy.env"
load_dotenv(env_path)
openai_api_key = os.getenv("OPENAI_API_KEY")

# MODEL = "qwen3.5-flash"
MODEL = "qwen3-max-2026-01-23"


# 大模型服务类封装
class QwenModel:
    def __init__(self, model_name=MODEL, temperature=0.7, streaming=True, **kwargs):
        # 初始化大模型实例
        self.model = ChatOpenAI(
            model=model_name,  # 模型名称
            api_key=openai_api_key,  # API 密钥
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # API 接口
            streaming=streaming,  # 流式输出
            temperature=temperature,  # 温度参数
            **kwargs  # 其他参数
        )

        # 保存参数信息，方便查看
        self.model_name = model_name
        self.temperature = temperature

    def invoke(self, messages):
        """
        调用大模型进行对话

        参数：
            messages: 消息列表，格式为 [{"role": "user", "content": "你好"}]

        返回：
            模型的响应结果
        """
        return self.model.invoke(messages)
