from langchain.agents import create_agent
from app.utils.Logger import Logger
from app.utils.model import QwenModel
from app.ai.tool.mysql_tool import mysql_tool
from app.ai.tool.send_email_tool import send_email
from app.ai.schema.email_reponse import EmailResponse


# 创建日志记录器
logger = Logger.get_logger(__name__)

"""
系统智能体：发送登录验证码
"""
class SystemAgent:
    def __init__(self):
        logger.info("初始化系统智能体")
        self.model = QwenModel().model
        self.tools = self.init_tools()
        self.agent = self.init_agent()
        self.register_agent = self.init_register_agent()

    # 初始化工具
    def init_tools(self):
        self.tools =[mysql_tool,send_email]
        return self.tools

    # 创建登录智能体
    def init_agent(self):
        # 提示词
        prompt = """
        一: 你是一个登录验证助手，你有两个工具
          1 mysql_tool 执行sql查询
          2 send_email 发送邮件

        二:工作流程：你必须严格按照以下步骤执行
          1 根据用户问题，调用 mysql_tool 工具查询 user_info 表确认邮箱是否存在
          2 【禁止自己生成任何验证码】必须使用用户传入的验证码
          3 调用 send_email 发送邮件，内容 = 传入的验证码

        三：反馈信息
          1 如果mysql_tool 工具验证邮箱失败，请返回状态码500，验证码为0，提示信息是：邮箱未注册
          2 如果 send_email 工具 发送邮件成功，请返回状态码200，验证码为本次传入的验证码，提示信息是：发送成功
          3 如果 send_email 工具 发送邮件失败，请返回状态码500，提示信息是：失败原因说明
        """
        # 创建登录智能体
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=prompt,
            debug=True,
            response_format=EmailResponse
        )
        return self.agent

    # 创建注册智能体
    def init_register_agent(self):
        # 注册提示词
        register_prompt = """
        一: 你是一个注册助手，你有两个工具
          1 mysql_tool 执行sql查询和插入
          2 send_email 发送邮件

        二:工作流程：你必须严格按照以下步骤执行
          1 根据用户问题，调用 mysql_tool 工具查询 user_info 表确认邮箱是否已存在
          2 如果邮箱已存在，请返回状态码500，提示信息是：邮箱已注册
          3 如果邮箱不存在，调用 mysql_tool 工具插入新用户记录到 user_info 表
          4 【禁止自己生成任何验证码】必须使用用户传入的验证码
          5 调用 send_email 发送邮件，内容 = 传入的验证码

        三：反馈信息
          1 如果邮箱已存在，请返回状态码500，提示信息是：邮箱已注册
          2 如果插入用户失败，请返回状态码500，提示信息是：注册失败
          3 如果 send_email 工具 发送邮件成功，请返回状态码200，验证码为本次传入的验证码，提示信息是：发送成功
          4 如果 send_email 工具 发送邮件失败，请返回状态码500，提示信息是：失败原因说明
        """
        # 创建注册智能体
        self.register_agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=register_prompt,
            debug=True,
            response_format=EmailResponse
        )
        return self.register_agent

    # 执行登录智能体
    def answer(self, email, code):
        prompt = f"用户邮箱：{email}，验证码：{code}"
        result = self.agent.invoke({"messages" :[{"role":"user","content":prompt}]})
        answer = result["structured_response"].model_dump()
        logger.info(f"系统智能体返回结果:{answer}")
        return answer

    # 执行注册智能体
    def register(self, email, code):
        prompt = f"用户邮箱：{email}，验证码：{code}"
        result = self.register_agent.invoke({"messages" :[{"role":"user","content":prompt}]})
        answer = result["structured_response"].model_dump()
        logger.info(f"注册智能体返回结果:{answer}")
        return answer


if __name__ == '__main__':
    agent = SystemAgent()
    agent.answer("用户邮箱为536001397@qq.com")


