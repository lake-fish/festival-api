# core/models.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class QueryRequest(BaseModel):
    """查询请求"""
    question: str = Field(..., description="用户问题，如'今年七夕是什么时候'")
    check_holiday: bool = Field(True, description="是否查询法定节假日安排")
    return_json: bool = Field(False, description="是否返回结构化JSON数据")


class SolarDate(BaseModel):
    """公历日期"""
    date: str = Field(..., description="YYYY-MM-DD格式")
    year: int
    month: int
    day: int
    week: int = Field(..., description="0=周日, 1=周一...")
    week_cn: str = Field(..., description="中文星期")


class LunarDate(BaseModel):
    """农历日期"""
    date_cn: str = Field(..., description="中文格式，如'七月初七'")
    year: int
    month: int
    day: int
    year_ganzhi: str = Field(..., description="干支年，如'丙午'")
    month_cn: str = Field(..., description="中文月")
    day_cn: str = Field(..., description="中文日")
    is_leap: bool = Field(False, description="是否闰月")


class HolidayInfo(BaseModel):
    """节假日信息"""
    is_legal: bool = Field(..., description="是否法定节假日")
    name: Optional[str] = Field(None, description="节日名称")
    rest_days: Optional[int] = Field(None, description="放假天数")
    wage: Optional[int] = Field(None, description="加班工资倍数")
    note: Optional[str] = Field(None, description="备注")


class QueryResponse(BaseModel):
    """查询响应"""
    success: bool = Field(..., description="是否成功")
    festival: str = Field(..., description="节日或节气名称")
    query_year: int = Field(..., description="查询年份")
    festival_type: Literal["lunar_fixed", "solar_fixed", "solar_term", "calculated"] = Field(..., description="节日类型：lunar_fixed=农历节日, solar_fixed=公历节日, solar_term=24节气, calculated=计算型节日（如母亲节、父亲节、感恩节）")

    solar: SolarDate
    lunar: LunarDate
    holiday: Optional[HolidayInfo] = Field(None, description="节假日信息")

    text: str = Field(..., description="友好文本回复")
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: str
    code: int = 400