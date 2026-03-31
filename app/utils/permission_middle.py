"""
验证用户角色权限：中间件
"""
from langchain.agents import AgentState
from langchain.agents.middleware import before_agent
from langgraph.runtime import Runtime
from app.utils.Logger import Logger
from app.utils.permission_role import permission_role

logger = Logger.get_logger(__name__)

@before_agent
def before_agent_middleware(state: AgentState, runtime: Runtime):
    print(state)
    # 获取用户ID
    user_id = state["messages"][0].user_id
    logger.info(f"用户id:{user_id}")
    # 查询用户角色
    role = permission_role(user_id)
    if role is None:
        raise Exception("用户不存在,请重新登录")
    if role != "总经理":
        raise Exception("用户权限不足")
    # 不做操作
    return None
