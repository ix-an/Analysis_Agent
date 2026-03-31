from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict
from app.utils.model import QwenModel

# 仅定义状态：存储问题+选中的智能体
class AgentState(TypedDict):
    question: str
    selected_agent: str

# 异步路由：只选智能体，不执行
async def route_agent(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是智能调度器，仅返回以下名称之一，无其他文字！
可选：sql_agent、analyze_agent、echarts_agent、file_agent"""),
        ("user", "问题：{question}")
    ])
    llm = QwenModel().model
    chain = prompt | llm
    response = await chain.ainvoke({"question": state["question"]})
    return {"selected_agent": response.content.strip()}

# 构建极简工作流：仅路由
def build_router_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("route", route_agent)
    workflow.set_entry_point("route")
    workflow.add_edge("route", END)
    return workflow.compile()

# 对外暴露：获取选中的智能体
async def get_selected_agent(question: str):
    app = build_router_workflow()
    result = await app.ainvoke({"question": question})
    return result["selected_agent"]