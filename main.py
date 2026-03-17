# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from core.models import QueryRequest, QueryResponse, ErrorResponse
from core.query import FestivalQuery


# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    app.state.query_engine = FestivalQuery()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} 启动成功")
    yield
    # 关闭时清理（如有需要）
    print("👋 服务关闭")


# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="农历/公历节日查询 API，支持阴阳历转换 + 法定节假日查询",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}


# 主查询接口
@app.post(
    "/api/v1/query",
    response_model=QueryResponse,
    responses={400: {"model": ErrorResponse}},
    tags=["Festival"]
)
async def query_festival(req: QueryRequest):
    """
    查询节日日期信息

    - **question**: 用户问题，如"今年七夕是什么时候"
    - **check_holiday**: 是否查询法定节假日安排（默认true）
    - **return_json**: 是否返回结构化数据（默认false，返回text字段）

    支持节日：春节/元宵/端午/七夕/中秋/重阳/腊八/元旦/万圣节/圣诞节等
    """
    try:
        engine: FestivalQuery = app.state.query_engine
        result = engine.query(
            question=req.question,
            check_holiday=req.check_holiday
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # 生产环境建议记录日志
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务异常: {str(e)}"
        )


# 批量查询接口（扩展）
@app.post("/api/v1/batch_query", tags=["Festival"])
async def batch_query(items: list[QueryRequest]):
    """批量查询多个节日（最多10个）"""
    if len(items) > 10:
        raise HTTPException(400, "单次最多查询10个节日")

    engine: FestivalQuery = app.state.query_engine
    results = []
    for req in items:
        try:
            results.append(engine.query(req.question, req.check_holiday))
        except Exception as e:
            results.append({
                'success': False,
                'error': str(e),
                'question': req.question
            })
    return {"results": results, "total": len(results)}


# 获取支持的节日列表
@app.get("/api/v1/festivals", tags=["Meta"])
async def list_festivals():
    """获取支持的节日列表"""
    from core.query import FestivalQuery
    return {
        "lunar_fixed": list(FestivalQuery.LUNAR_FESTIVALS.keys()),
        "solar_fixed": list(FestivalQuery.SOLAR_FESTIVALS.keys()),
        "legal_holidays": list(FestivalQuery.LEGAL_HOLIDAYS)
    }


# 根路径重定向到文档
@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal Server Error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # 开发环境开启热重载
        log_level="info"
    )