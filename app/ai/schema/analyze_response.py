from pydantic import BaseModel,Field
"""
数据表格响应类
"""
class TableResponse(BaseModel):
    column_name: list = Field(..., description="英文表头")
    data:list[dict[str, str]] = Field(..., description="数据")
"""
数据分析响应类
"""
class AnalyzeResponse(BaseModel):
    table:TableResponse = Field(...,description="表格数据")
    result:str = Field(...,description="分析结果")
    json:str = Field(...,description="图表数据")