from pydantic import BaseModel,Field
"""
echarts 图表响应类
"""
class EchartsResponse(BaseModel):

    json: str = Field(..., description="json数据")
    code: int = Field(..., description="状态码")
    msg: str = Field(..., description="提示信息")