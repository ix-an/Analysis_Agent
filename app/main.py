from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.Logger import Logger
from app.ai.agent.system_agent import SystemAgent
# from app.ai.agent.sql_qa_agent import SqlAgent
from app.ai.agent.sql_qa_agent_pg import SqlAgentPg  # 添加PostgresSQL记忆的sql问答智能体类
from app.ai.agent.echarts_agent import EchartsAgent  # 添加Echarts图表生成智能体类
from app.ai.agent.analyze_agent import AnalyzeAgent  # 添加数据分析智能体类
from app.ai.agent.file_analyze_agent import FileAnalyzeAgent  # 添加文件数据分析智能体类
from app.api.system.system_router import system_router
from app.api.chat.chat_router import chat_router
import uvicorn
import sys
from fastapi.staticfiles import StaticFiles  # 静态文件依赖
from pathlib import Path

# 创建日志记录器
logger = Logger.get_logger(__name__)

"""
智能体在服务器模式下单例加载
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时初始化聊天智能体
    app.state.system_agent = SystemAgent()
    # app.state.sql_agent = SqlAgent()
    app.state.sql_agent_pg = SqlAgentPg()
    app.state.echarts_agent = EchartsAgent()
    app.state.analyze_agent = AnalyzeAgent()
    app.state.file_analyze_agent = FileAnalyzeAgent()
    logger.info("系统智能体实例创建成功")
    # logger.info("sql问答智能体实例创建成功")
    logger.info("sql问答 PostgresSQL记忆智能体实例创建成功")
    logger.info("Echarts图表生成智能体实例创建成功")
    logger.info("数据分析智能体实例创建成功")
    logger.info("文件数据分析智能体实例创建成功")
    yield  # 应用停止时清理
    logger.info("系统智能体实例销毁成功")
    # logger.info("sql问答智能体实例销毁成功")
    logger.info("sql问答 PostgresSQL记忆智能体实例销毁成功")
    logger.info("Echarts图表生成智能体实例销毁成功")
    logger.info("数据分析智能体实例销毁成功")
    logger.info("文件数据分析智能体实例销毁成功")


# 创建 FastAPI 实例
app = FastAPI(lifespan=lifespan)

# 跨域配置，添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- 注册路由 ----------
app.include_router(system_router)  # 注册系统路由
app.include_router(chat_router)  # 注册聊天路由

# 挂载静态文件目录
base_dir = Path(__file__).resolve().parent  # 项目根目录
app.mount(
    "/static",
    StaticFiles(directory=base_dir / "static"),
    name="static"
)


if __name__ == '__main__':
    # 启动服务
    # uvicorn.run(app, host="localhost", port=8000)
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--loop", "asyncio", "--port", "8000"]
    import subprocess
    subprocess.run(cmd)
