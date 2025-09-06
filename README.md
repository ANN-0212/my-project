# weather

## 介绍
基于Flask的气象数据采集与可视化平台

## 软件架构
### 核心功能模块
- **数据采集**：支持多API数据获取与本地存储
- **数据可视化**：提供丰富的气象数据可视化图表
- **用户系统**：支持登录注册与城市收藏功能
- **预测分析**：集成7天天气预测模型

### 目录结构
```
weather_ai/
├── app/                      # 应用核心代码
│   ├── __init__.py           # 应用初始化
│   ├── models.py             # 数据模型定义
│   ├── routes/               # 路由模块
│   │   ├── weather.py        # 天气数据路由
│   │   └── visualization.py  # 可视化路由
│   ├── utils/                # 工具模块
│   │   ├── weather_crawler.py # 数据采集器
│   │   └── advanced_predictor.py # 数据分析器
│   └── templates/            # 前端模板
│       ├── dashboard.html    # 主仪表盘
│       ├── home.html         # 首页
│       └── 7days_forecast.html # 天气预报页
├── config.py                 # 配置文件
├── requirements.txt          # 依赖列表
├── run.py                   # 应用启动入口
```

## 功能特性
1. **多源数据采集**
   - 支持OpenWeatherMap、Weatherbit等多API数据获取
   - 提供本地数据回退机制
   - 支持全量/单个城市数据采集

2. **数据可视化**
   - 温度、湿度、风速趋势图表
   - 城市对比分析功能
   - 历史数据可视化展示

3. **预测分析**
   - 集成7天天气预测模型
   - 支持极端天气预警
   - 提供默认预测策略

4. **用户系统**
   - 登录注册功能
   - 城市收藏管理
   - 数据导出(CSV)

## 环境要求
- Python 3.8+
- MySQL 5.7+
- Redis (可选，用于缓存)
- 支持的API服务：
  - OpenWeatherMap
  - Weatherbit

## 安装指南
1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置数据库
```bash
# 修改config.py中的数据库连接信息
DATABASE_URI = "mysql://user:password@localhost:3306/weather_db"
```

3. 初始化数据库
```bash
flask init-db
```

4. 启动应用
```bash
python run.py
```

## 使用说明
1. 数据采集
```bash
# 采集所有城市数据
curl http://localhost:5000/crawl/all

# 采集指定城市数据
curl http://localhost:5000/crawl/<city_name>
```

2. 数据可视化
- 访问仪表盘：http://localhost:5000/dashboard
- 查看7天预报：http://localhost:5000/7days_forecast
- 城市对比分析：http://localhost:5000/api/city_comparison

3. 数据导出
```bash
# 导出指定城市CSV数据
curl http://localhost:5000/export/csv/<city>
```

## API文档
### 天气数据接口
- `GET /api/weather/temperature_trend` - 温度趋势数据
- `GET /api/weather/humidity_trend` - 湿度趋势数据
- `GET /api/weather/wind_trend` - 风速趋势数据
- `GET /api/weather/city_comparison` - 城市对比数据

### 可视化接口
- `GET /api/temperature_trend` - 实时温度趋势
- `GET /api/humidity_trend` - 实时湿度趋势
- `GET /api/wind_trend` - 实时风速趋势
- `GET /api/current_weather` - 当前天气概览

## 致谢
- 感谢 OpenWeatherMap 提供气象数据API
- 感谢 ECharts 提供优秀的数据可视化库
- 感谢 Flask 团队开发了轻量高效的Web框架
- 感谢 Weatherbit 提供备用数据源

## 许可证
本项目采用 MIT License，详情请参阅 LICENSE 文件。
