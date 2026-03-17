# Festival Query API

农历/公历节日查询服务，支持阴阳历转换 + 法定节假日查询。

基于 [lunar-python](https://github.com/6tail/lunar-python) 和 [提莫节假日 API](https://timor.tech/api/holiday) 开发。

## ✨ 功能特性

- 🎊 支持农历和公历节日查询
- 🌿 支持24节气日期查询（如"芒种是几月几号"、"去年大寒是什么时候"）
- 📅 自动进行阴阳历日期转换
- 🏖️ 集成法定节假日信息查询
- 🔍 智能解析自然语言问题（如"今年七夕是什么时候"）
- 📝 支持年份关键词：今年、去年、明年、具体年份
- 🎯 支持节日别名识别（如"中秋节"、"七夕节"等）

## 🚀 快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

### 3. 访问 API 文档

启动后访问：http://localhost:8000/docs

## 📖 API 文档

### 1. 查询节日日期

**接口地址：** `POST /api/v1/query`

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | 是 | 用户问题，如"今年七夕是什么时候" |
| check_holiday | boolean | 否 | 是否查询法定节假日安排（默认 true） |

**请求示例：**

#### cURL

```bash
# 查询今年七夕节
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "今年七夕节是什么时候",
    "check_holiday": true
  }'

# 查询去年中秋节
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "去年中秋节是什么时候"
  }'

# 查询今年万圣节
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "今年万圣节是什么时候",
    "check_holiday": false
  }'

# 查询今年芒种节气
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "今年芒种是几月几号"
  }'

# 查询去年大寒节气
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "去年大寒是什么时候"
  }'
```

#### Python

```python
import requests

# 查询今年七夕节
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "question": "今年七夕节是什么时候",
        "check_holiday": True
    }
)
result = response.json()
print(result)

# 查询去年中秋节
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "question": "去年中秋节是什么时候"
    }
)
print(response.json())

# 查询明年春节
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "question": "明年春节是什么时候"
    }
)
print(response.json())

# 查询今年芒种节气
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "question": "今年芒种是几月几号"
    }
)
print(response.json())

# 查询去年大寒节气
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "question": "去年大寒是什么时候"
    }
)
print(response.json())
```

#### JavaScript (fetch)

```javascript
// 查询今年七夕节
fetch('http://localhost:8000/api/v1/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: '今年七夕节是什么时候',
    check_holiday: true
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

**响应示例：**

```json
{
  "success": true,
  "festival": "七夕",
  "query_year": 2026,
  "festival_type": "lunar_fixed",
  "solar": {
    "date": "2026-08-19",
    "year": 2026,
    "month": 8,
    "day": 19,
    "week": 3,
    "week_cn": "三"
  },
  "lunar": {
    "date_cn": "七月初七",
    "year": 2026,
    "month": 7,
    "day": 7,
    "year_ganzhi": "丙午",
    "month_cn": "七月",
    "day_cn": "初七",
    "is_leap": false
  },
  "holiday": null,
  "text": "🎊 七夕\n📅 公历：2026-08-19（星期三）\n🌙 农历：丙午年 七月初七\nℹ️ 传统节日（当年不放假）",
  "timestamp": "2026-01-17T10:30:00"
}
```

### 2. 批量查询节日

**接口地址：** `POST /api/v1/batch_query`

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| items | array | 是 | 查询请求数组（最多10个） |

**请求示例：**

```bash
curl -X POST "http://localhost:8000/api/v1/batch_query" \
  -H "Content-Type: application/json" \
  -d '[
    {"question": "今年春节是什么时候"},
    {"question": "今年中秋节是什么时候"},
    {"question": "今年万圣节是什么时候"}
  ]'
```

**响应示例：**

```json
{
  "results": [
    {
      "success": true,
      "festival": "春节",
      "query_year": 2026,
      ...
    },
    ...
  ],
  "total": 3
}
```

### 3. 获取支持的节日列表

**接口地址：** `GET /api/v1/festivals`

**请求示例：**

```bash
curl "http://localhost:8000/api/v1/festivals"
```

**响应示例：**

```json
{
  "lunar_fixed": [
    "春节", "元宵", "龙头节", "花朝节", "上巳", "端午",
    "七夕", "中元", "中秋", "重阳", "下元", "腊八", "小年", "除夕"
  ],
  "solar_fixed": [
    "元旦", "情人节", "妇女节", "植树节", "愚人节", "劳动节",
    "青年节", "儿童节", "建党节", "建军节", "教师节", "国庆节",
    "万圣节", "光棍节", "平安夜", "圣诞节"
  ],
  "solar_terms": [
    "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
    "立夏", "小满", "芒种", "夏至", "小暑", "大暑",
    "立秋", "处暑", "白露", "秋分", "寒露", "霜降",
    "立冬", "小雪", "大雪", "冬至", "小寒", "大寒"
  ],
  "legal_holidays": [
    "春节", "清明", "劳动节", "端午", "中秋", "国庆", "元旦"
  ]
}
```

### 4. 健康检查

**接口地址：** `GET /health`

**请求示例：**

```bash
curl "http://localhost:8000/health"
```

**响应示例：**

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

## 🎯 支持的节日

### 农历节日

- **春节** (正月初一)
- **元宵** (正月十五)
- **龙头节** (二月初二)
- **花朝节** (二月十二)
- **上巳** (三月初三)
- **端午** (五月初五)
- **七夕** (七月初七)
- **中元** (七月十五)
- **中秋** (八月十五)
- **重阳** (九月初九)
- **下元** (十月十五)
- **腊八** (腊月初八)
- **小年** (腊月二十三)
- **除夕** (腊月二十九/三十)

### 公历节日

- **元旦** (1月1日)
- **情人节** (2月14日)
- **妇女节** (3月8日)
- **植树节** (3月12日)
- **愚人节** (4月1日)
- **劳动节** (5月1日)
- **青年节** (5月4日)
- **儿童节** (6月1日)
- **建党节** (7月1日)
- **建军节** (8月1日)
- **教师节** (9月10日)
- **国庆节** (10月1日)
- **万圣节** (10月31日)
- **光棍节** (11月11日)
- **平安夜** (12月24日)
- **圣诞节** (12月25日)

### 24节气

- **春季**：立春、雨水、惊蛰、春分、清明、谷雨
- **夏季**：立夏、小满、芒种、夏至、小暑、大暑
- **秋季**：立秋、处暑、白露、秋分、寒露、霜降
- **冬季**：立冬、小雪、大雪、冬至、小寒、大寒

> 注意：节气日期每年略有不同，系统会自动计算准确的公历和农历日期。

### 支持的别名

- 中秋节 → 中秋
- 端午节 → 端午
- 重阳节 → 重阳
- 元宵节 → 元宵
- 腊八节 → 腊八
- 万圣节前夜 → 万圣节
- 圣诞夜 → 平安夜

## 💡 使用示例

### 示例 1：查询今年七夕节

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "今年七夕节是什么时候"}'
```

### 示例 2：查询去年中秋节（带法定节假日信息）

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "去年中秋节是什么时候", "check_holiday": true}'
```

### 示例 3：查询明年春节

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "明年春节是什么时候"}'
```

### 示例 4：查询今年万圣节（不查询法定节假日）

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "今年万圣节是什么时候", "check_holiday": false}'
```

### 示例 5：查询今年芒种节气

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "今年芒种是几月几号"}'
```

### 示例 6：查询去年大寒节气

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "去年大寒是什么时候"}'
```

### 示例 7：查询今年清明节气（法定节假日）

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "今年清明是几月几号", "check_holiday": true}'
```

## 🔧 技术栈

- **FastAPI** - 现代、快速的 Web 框架
- **lunar-python** - 农历转换库
- **提莫节假日 API** - 法定节假日信息
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI 服务器

## 📝 项目结构

```
festival-api/
├── main.py              # FastAPI 应用入口
├── config.py            # 配置管理
├── requirements.txt     # 依赖列表
├── README.md           # 项目文档
└── core/
    ├── __init__.py
    ├── models.py        # 数据模型
    ├── query.py         # 核心查询逻辑
    └── cache.py         # 缓存实现
```

## ⚙️ 配置说明

可以通过环境变量或 `.env` 文件配置：

```env
# 服务配置
HOST=0.0.0.0
PORT=8000

# API 配置
TIMOR_API_BASE=https://timor.tech/api/holiday
REQUEST_TIMEOUT=5

# 缓存配置（秒）
CACHE_TTL=3600
```

## 📄 许可证

MIT License

## 🙏 致谢

- [lunar-python](https://github.com/6tail/lunar-python) - 农历转换库
- [提莫节假日 API](https://timor.tech/api/holiday) - 免费节假日 API 服务

## 📮 反馈与贡献

欢迎提交 Issue 和 Pull Request！
