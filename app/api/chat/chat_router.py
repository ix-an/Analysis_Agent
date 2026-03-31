from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.utils.Logger import Logger
import json
from fastapi import UploadFile, File
import os
from app.ai.tool.agent_workflow import  get_selected_agent

logger = Logger.get_logger(__name__)
chat_router = APIRouter()

# 核心聊天接口：智能路由 + 原生流式输出
@chat_router.get("/chat")
async def chat(request: Request, question: str, user_id: str):
    try:
        # 1. LangGraph智能选择智能体（LLM路由，替代关键字）
        agent_name = await get_selected_agent(question)
        logger.info(f"LLM路由选中：{agent_name}")

        # 2. 获取你原有的智能体实例
        agents = {
            "sql_agent": request.app.state.sql_agent_pg,
            "analyze_agent": request.app.state.analyze_agent,
            "echarts_agent": request.app.state.echarts_agent,
            "file_agent": request.app.state.file_analyze_agent
        }
        target_agent = agents.get(agent_name, agents["sql_agent"])

        # 3. ✅ 关键：直接透传你原有智能体的流式生成器（完美恢复流式）
        async def stream_response():
            async for chunk in target_agent.answer(question, user_id):
                yield f"data:{json.dumps({'content': chunk, 'done': False})}\n\n"
            yield f"data:{json.dumps({'content': '', 'done': True})}\n\n"

        return StreamingResponse(stream_response(), media_type="text/event-stream")

    except Exception as e:
        async def error_stream():
            yield f"data:{json.dumps({'content': f'错误：{str(e)}', 'done': True, 'error': True})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

# 文件上传接口（完全不动）
@chat_router.post("/upload")
async def upload(file: UploadFile = File(...)):
    upload_dir = "static/upload"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    logger.info(f"上传文件：{file_path}")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"code": 200, "filename": file.filename}